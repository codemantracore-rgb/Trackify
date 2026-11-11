#redis Hit and Miss Functions 
from django.core.cache import cache

def _safe_cache_key(key):
    try:
        return cache.get(key)
    except :
        pass
def _set_cache(key,value,timeout):
    try:
        cache.set(key,value,timeout)
    except:
        pass
def _delete_cache(user_id):
    try:
        cache.delete(f'trackify:preferences:v1:{user_id}')
    except:
        pass


# Strength and Category Seperation LangWise, GenreWise, ArtistWise 
from .models import UserPrefrence
from collections import defaultdict
SET_TIMEOUT_PREFRENCE=30
def _UserCategoryPrefrence(user):
    user_id=key = f'trackify:preferences:v1:{user.pk}'
    cached=_safe_cache_key(user_id)
    if cached is not None:
        return cached
    
    

    total={_:defaultdict(float) for _ in ('genre','language','artist')}
    events=(
        # Currently in this case It also retrives Other user prefrrences ; Used for trending Songs Track  
        # UserPrefrence.objects.select_related('music').prefetch_related('music__language','music__genre','music__artist')[:50]
                UserPrefrence.objects.filter(user=user,music__isnull=False).select_related('music').prefetch_related('music__language','music__genre','music__artist')[:50]

    )
    for index,event in enumerate(events):
        #Logic for Recentivity Of Event For Suggestion
        strength=1.0
        recent_weight=max(1.0,1.0-(index/500.0)*0.75)
        if event.completed:
            strength+=1.0
        if event.liked:
            strength+=2.0
        if event.skipped:
            continue
        strength*=recent_weight

        music=event.music
        for language in music.language.all():
            total['language'][language.name]+=strength
        for genre in music.genre.all():
            total['genre'][genre.type]+=strength
        for artist in music.artist.all():
            total['artist'][artist.name]+=strength

    prefrence={}
    for category,amt in total.items():
        total=sum(amt.values())
        prefrence[category]=(
            {
              name: round(value/total,6)  for name,value in amt.items()
            }
            if total else {}
        )

    _set_cache(user_id,prefrence,SET_TIMEOUT_PREFRENCE)
    return prefrence



def music_score(music,prefrences):
    language_names=[obj.name for obj in music.language.all()]
    genre_names=[obj.type for obj in music.genre.all()]
    artist_names=[obj.name for obj in music.artist.all()]

    language_score=_average_finder_prefrences(language_names,prefrences['language'])
    genre_score=_average_finder_prefrences(genre_names,prefrences['genre'])
    artist_score=_average_finder_prefrences(artist_names,prefrences['artist'])

    return (0.45 *language_score )+ (0.35*genre_score) + (0.20*artist_score)

# from datetime import timezone
from django.utils import timezone
import hashlib
def _exploration_key(user_id,music):
    token=f'{user_id}:{timezone.localdate().isoformat()}:{music}'.encode()
    return hashlib.sha256(token).hexdigest()


def _average_finder_prefrences(names,prefrences):
    if not names or not prefrences:
        return 0.0
    return sum(prefrences.get(name,0.0) for name in names)/len(names)

#Arranges Playlist as per 80% Prefrence and 20% exploring
def _interleave(persionalized,exploration):# Merge 2-Sorted array DSA 
    result=[]
    used=set()
    p_index=e_index=0
    while p_index<len(persionalized) or e_index<len(exploration):
        for _ in range(4):
            #Logic for 4 prefred
            while p_index< len(persionalized) and persionalized[p_index].pk in used:
                p_index+=1
            if p_index<len(persionalized):
                item=persionalized[p_index]
                result.append(item)
                used.add(item.pk)
                p_index+=1
        #logic for one exploration
        while e_index<len(exploration) and exploration[e_index].pk in used:
                e_index+=1
        if e_index<len(exploration):
            item=exploration[e_index]
            result.append(item)
            used.add(item.pk)
            e_index+=1
    return result
        
# preparing Persionized and Exploration Songs and then returning merged and final one
def order_music_for_user(user,queryset):
    if not getattr(user,'is_authenticated',False):
        return list(queryset)
    prefrences=_UserCategoryPrefrence(user)
    if not any(prefrences.values()):
        return list(queryset)
    # skipped_ids = {
    # music_id
    # for music_id, event in latest_event_by_music.items()
    # if event.skipped
    # }
    songs=list(
        # in queryset Music Models is passed
        queryset.prefetch_related('language','artist','genre')
    )
    
    scored_songs=[ (music_score(song,prefrences),song) for song in songs]
    persionalized=[
        song for score,song in sorted(scored_songs, key=lambda pair:(-pair[0],pair[1].id))

    ]
    #exploring key ensures same pagination throughout day 
    exploring=sorted(songs,key=lambda song :_exploration_key(user.pk,song.pk))
    return _interleave(persionalized,exploring)




