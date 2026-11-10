
import random
import uuid

from faker import Faker
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import (
    Language,
    Artist,
    Genre,
    Music,
    Playlist,
    PlayListTrack,
)

fake = Faker("en_IN")


@transaction.atomic
def seed_data(total):

    print("Starting music database seeding...")

    # ---------------------------------
    # 1. CREATE LANGUAGES
    # ---------------------------------

    language_names = [
        "Hindi",
        "English",
        "Gujarati",
        "Punjabi",
        "Tamil",
        "Telugu",
        "Bengali",
        "Marathi",
        "Malayalam",
        "Kannada",
    ]

    languages = []

    for name in language_names:

        language, created = Language.objects.get_or_create(
            name=name
        )

        languages.append(language)

    print(f"{len(languages)} languages ready")


    # ---------------------------------
    # 2. CREATE ARTISTS
    # ---------------------------------

    artists = []

    for i in range(20):

        artist, created = Artist.objects.get_or_create(
            name=fake.unique.name()
        )

        # Assign 1 to 3 languages
        artist_languages = random.sample(
            languages,
            k=random.randint(1, 3)
        )

        artist.language.add(*artist_languages)

        artists.append(artist)

    print(f"{len(artists)} artists ready")


    # ---------------------------------
    # 3. CREATE GENRES
    # ---------------------------------

    genre_names = [
        "Pop",
        "Rock",
        "Classical",
        "Hip Hop",
        "Jazz",
        "Romantic",
        "Devotional",
        "Electronic",
        "Folk",
        "Indie",
    ]

    genres = []

    for name in genre_names:

        genre, created = Genre.objects.get_or_create(
            type=name
        )

        genre_artists = random.sample(
            artists,
            k=random.randint(2, 5)
        )

        genre.artist.add(*genre_artists)

        genres.append(genre)

    print(f"{len(genres)} genres ready")


    # ---------------------------------
    # 4. CREATE MUSIC
    # ---------------------------------

    music_records = []

    for i in range(50):

        selected_artists = random.sample(
            artists,
            k=random.randint(1, 3)
        )

        selected_languages = random.sample(
            languages,
            k=random.randint(1, 2)
        )

        selected_genres = random.sample(
            genres,
            k=random.randint(1, 3)
        )

        # Temporary unique hash
        music = Music.objects.create(

            title=f"{fake.sentence(nb_words=3).rstrip('.')} {i}",

            description=fake.text(max_nb_chars=300),

            duration=random.randint(120, 360),

            file_size=random.randint(
                2_000_000,
                15_000_000
            ),

            bitrate=random.choice([
                128000,
                192000,
                256000,
                320000
            ]),

            samples=random.choice([
                44100,
                48000
            ]),

            channels=random.choice([1, 2]),

            is_active=fake.boolean(chance_of_getting_true=90),

            unique_hash=uuid.uuid4().hex
        )

        # Assign ManyToMany relationships
        music.artist.set(selected_artists)

        music.language.set(selected_languages)

        music.genre.set(selected_genres)

        # Generate actual hash AFTER setting relationships
        generated_hash = music.generate_unique_hash()

        # Avoid duplicate music hash
        duplicate = Music.objects.filter(
            unique_hash=generated_hash
        ).exclude(pk=music.pk).exists()

        if duplicate:
            music.delete()
            continue

        music.unique_hash = generated_hash

        music.save(update_fields=["unique_hash"])

        music_records.append(music)

    print(f"{len(music_records)} music records created")


    # ---------------------------------
    # 5. CREATE PLAYLISTS
    # ---------------------------------

    User = get_user_model()

    users = list(User.objects.all()[:5])

    playlists = []

    if not users:

        print(
            "No users found. Skipping playlist creation."
        )

    else:

        for user in users:

            for i in range(2):

                playlist = Playlist.objects.create(

                    user=user,

                    title=fake.sentence(nb_words=3),

                    is_public=fake.boolean()
                )

                playlists.append(playlist)

        print(f"{len(playlists)} playlists created")


    # ---------------------------------
    # 6. CREATE PLAYLIST TRACKS
    # ---------------------------------

    playlist_tracks = []

    if music_records:

        for playlist in playlists:

            selected_music = random.sample(
                music_records,
                k=min(
                    random.randint(3, 10),
                    len(music_records)
                )
            )

            for position, music in enumerate(
                selected_music,
                start=1
            ):

                playlist_tracks.append(
                    PlayListTrack(
                        playlist=playlist,
                        music=music,
                        position=position
                    )
                )

    PlayListTrack.objects.bulk_create(playlist_tracks)

    print(
        f"{len(playlist_tracks)} playlist tracks created"
    )

    print("Music database seeding completed!")
