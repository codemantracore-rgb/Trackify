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
        cache.delete(f'tracify:prefrerences:v1:{user_id}')
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
    
    

    total={defaultdict(float) for _ in ('Genre','Language','Artist')}
    events=(
        UserPrefrence.objects.filter('music').prefetch_realted('music__language','music__genre','music__artist')[:50]
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
            strength*=0.2
        strength*=recent_weight

        music=event.music
        for language in music.objects.all():
            total['language'][language.name]+=strength
        for genre in music.objects.all():
            total['genre'][genre.name]+=strength
        for artist in music.objects.all():
            total['artist'][artist.name]+=strength

    prefrence={}
    for category,amt in totals.items():
        total=sum(amt.values())
        prefrences[category]=(
            {
              name: round(value/total,6)  for name,value in values.items()
            }
            if total else {}
        )

    _set_cache(user,prefrence,SET_TIMEOUT_PREFRENCE)
    return prefrence

#Arranges Playlist as per 80% Prefrence and 20% exploring
def _interleave(persionalized,exploration):# Merge 2-Sorted array DSA 
    result=[]
    used=set()
    p_index=e_index=0
    while p_index<len(persionalized) and e_index<len(exploration):
        for _ in range(4):
            #Logic for 4 prefred
            while p_index>0 and persionalized[p_index].pk in used:
                p_index+=1
            if p_index<len(persionalized):
                item=persionalized[p_index]
                result.append(item)
                used.add(item.pk)
                p_index+=1
        #logic for one exploration
        while e_index>0 and exploration[e_index].pk in used:
                e_index+=1
        if e_index<len(exploration):
            item=exploration[e_index]
            result.append(item)
            used.add(item.pk)
            e_index+=1
    return result
        
