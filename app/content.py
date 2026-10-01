"""Editorial copy for mood and genre pages. Hand-written, unique per page - no templated filler."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PageContent:
    title: str
    description: str
    blurb: str
    intro: tuple[str, ...] = ()
    faq: tuple[tuple[str, str], ...] = ()


MOODS: dict[str, PageContent] = {
    "sad": PageContent(
        "Best Sad Movies to Watch Tonight",
        "Sad movies for when you want to feel it, not fix it: emotional dramas, quiet heartbreakers and bittersweet stories, ranked by rating.",
        "Quiet heartbreakers and bittersweet stories",
        ("Sometimes you want a movie that matches your mood rather than trying to change it. These are films that take sadness seriously: grief, distance, things that ended too soon, told without rushing you toward a happy ending.",
         "Most of them are slow and character-driven, so they work best when you have the evening free and the phone in another room."),
        (("What's a good movie to watch when you're feeling sad?",
          "Pick a film that meets you where you are rather than one that tries to cheer you up. A quiet drama about loss or distance often helps more than a comedy. If you want to feel lighter by the end, look for movies that are also tagged emotional or happy."),
         ("Is it okay to watch a sad movie when you're already down?",
          "For many people, yes: a sad story can make a heavy feeling easier to name. If it starts making things worse, stop, put on something from the cozy or chill pages, and talk to someone you trust.")),
    ),
    "happy": PageContent(
        "Feel-Good Movies to Watch When You Want to Smile",
        "Happy, feel-good movies that leave you lighter than they found you: warm comedies, uplifting stories and crowd-pleasers, ranked by rating.",
        "Warm, bright films that leave you lighter",
        ("Happy movies do one job well: you finish them in a better mood than you started. Expect warm characters, jokes that land and endings that feel earned instead of forced.",
         "If you can't decide, start near the top of the list. These are the films most viewers rated highly and would happily watch again."),
        (("What should I watch to feel happier?",
          "Look for movies tagged happy and funny at the same time, with a runtime under two hours. Short, warm stories with likeable characters lift a mood faster than big ensemble epics."),
         ("What's a good feel-good movie for the whole family?",
          "Animation and adventure are the safest places to start. Check the age rating on your streaming service before you press play, since we don't list it.")),
    ),
    "romantic": PageContent(
        "Romantic Movies for a Night In",
        "Romantic movies beyond the clichés: slow-burn love stories, bittersweet romances and date-night picks, ranked by rating.",
        "Slow-burn love stories and date-night picks",
        ("Romance covers a lot of ground: first crushes, long marriages, love that arrives at the wrong time. This list leans toward films where the relationship is the story, not a subplot.",
         "Watching with someone? Check the runtime first. A two-hour romance on a work night lands very differently than on a Saturday."),
        (("What's a good romantic movie for a first date?",
          "Choose something light and under two hours, so you're not committed to a long, heavy mood. A romantic comedy leaves room to talk afterwards, which a tragedy doesn't."),
         ("What are good romantic movies if I don't like cheesy ones?",
          "Look for romances that are also tagged emotional or atmospheric. They tend to be quieter, more honest about relationships and less dependent on a grand gesture.")),
    ),
    "lonely": PageContent(
        "Movies for When You're Feeling Lonely",
        "Movies for lonely nights: quiet films about isolation, connection and finding company in a story. Ranked by rating, no account needed.",
        "Company for a quiet night alone",
        ("Being alone and feeling lonely aren't the same thing, and the best films about it know that. These are stories about distance, solitude and the odd comfort of watching someone else feel it too.",
         "Some are gentle, some are heavy. Read the mood tags on each card to choose between company and catharsis."),
        (("What should I watch when I'm lonely?",
          "Try a film with a warm center: characters who find each other, even briefly. If you'd rather not be reminded of the feeling, pick something from the cozy or chill moods instead."),
         ("Can a movie help with loneliness?",
          "A good story can feel like company for a couple of hours, but it isn't a substitute for people. If the feeling lasts for weeks, talking to a friend or a professional is a better next step than another movie.")),
    ),
    "dark": PageContent(
        "Dark Movies: Bleak, Tense and Unsettling",
        "Dark movies for people who like their stories bleak: morally grey thrillers, crime dramas and unsettling mysteries, ranked by rating.",
        "Bleak, morally grey and unsettling",
        ("Dark doesn't have to mean horror. These are films with a heavy atmosphere: moral grey zones, crime that costs something, endings that don't forgive anyone.",
         "Good for late evenings. Probably not the best pick if you're already feeling low."),
    ),
    "funny": PageContent(
        "Funny Movies That Actually Make You Laugh",
        "Funny movies for a laugh-out-loud night: sharp comedies, awkward situations and dry humor, ranked by rating and tagged by mood.",
        "Comedies worth a real laugh",
        ("Comedy is the most personal genre, so this list leans on ratings from many viewers rather than one critic's taste. Some of these are loud, some are dry as toast.",
         "If a film hasn't landed in the first twenty minutes, it probably won't. Move on to the next one."),
        (("What's a good funny movie to watch with friends?",
          "Pick something broad and quotable rather than subtle. Ensemble comedies work best because everyone finds a different joke funny."),
         ("What should I watch if I want to laugh but also feel something?",
          "Look for comedies that are also tagged emotional or happy. They're funny first, but they have a heart that makes the ending land.")),
    ),
    "cozy": PageContent(
        "Cozy Movies for Blankets and Rainy Evenings",
        "Cozy movies for blankets, tea and rainy evenings: gentle stories, small-town charm and low-stakes comfort, ranked by rating.",
        "Blankets, tea and low-stakes comfort",
        ("Cozy films are low on stakes and high on atmosphere: small towns, warm kitchens, characters you'd like as neighbors. Nothing here is trying to wear you out.",
         "They also rewatch well. Keep a couple in reserve for the days you don't want to risk a new favorite."),
    ),
    "atmospheric": PageContent(
        "Atmospheric Movies for Late Nights",
        "Atmospheric movies for late nights: slow, immersive films where mood, sound and visuals matter as much as the plot. Ranked by rating.",
        "Slow, immersive films for late nights",
        ("These are films you feel more than follow: long shots, patient pacing, sound design that fills the room. The plot sometimes takes a back seat to the place and the mood.",
         "Best watched in the dark with decent speakers or headphones, phone elsewhere."),
        (("What's a good atmospheric movie for a late night?",
          "Choose something slow and visual, with a runtime you can finish before you're too tired. Sci-fi, mystery and quiet drama are the usual places to look."),
         ("What makes a movie atmospheric?",
          "Mood is built through setting, music, lighting and pacing rather than dialogue and plot twists. If you remember how a film felt more than what happened in it, it was probably atmospheric.")),
    ),
    "emotional": PageContent(
        "Emotional Movies That Stay With You",
        "Emotional movies that stay with you: moving dramas about family, love and loss, ranked by rating and tagged by mood.",
        "Moving stories about love, family and loss",
        ("Emotional films earn their tears. They're about love, family, regret and second chances, and the good ones are specific enough that you feel the story as your own.",
         "Keep tissues nearby, and give yourself some time afterwards. A few of these deserve a quiet half hour before you do anything else."),
    ),
    "thought-provoking": PageContent(
        "Thought-Provoking Movies Worth Talking About",
        "Thought-provoking movies that raise questions long after the credits: ideas-driven dramas, sci-fi and documentaries, ranked by rating.",
        "Films that keep you thinking afterwards",
        ("These films leave questions behind: about choices, society, memory or what a good life even is. They rarely hand you the answer, and the best ones change what you ask.",
         "Watch with someone if you can. Half the value is the conversation afterwards."),
        (("What's a good thought-provoking movie to watch alone?",
          "Pick something with a clear central idea rather than a twisty plot, so you can think about it afterwards instead of just decoding it. Drama and documentary work best."),
         ("What's the difference between thought-provoking and mind-bending?",
          "Thought-provoking films raise questions about life and society. Mind-bending films play with reality, time or identity. The lists overlap, but mind-bending ones care more about the puzzle.")),
    ),
    "motivational": PageContent(
        "Motivational Movies to Get You Moving",
        "Motivational movies for when you need a push: underdog stories, hard-won victories and people who refuse to quit. Ranked by rating.",
        "Underdogs, comebacks and second chances",
        ("Motivational films are about effort: someone starts far behind, keeps going, and the film doesn't pretend it was easy. They work best before a big week, not after one.",
         "Pick one with a runtime you can finish today. A motivating film you abandon halfway does the opposite."),
    ),
    "scary": PageContent(
        "Scary Movies for a Good Fright",
        "Scary movies, from slow dread to jump scares: horror and thrillers ranked by rating and tagged by mood, so you can pick your kind of fear.",
        "From slow dread to jump scares",
        ("Fear comes in flavors: slow dread, jump scares, haunted places, people who are worse than monsters. Check the mood tags to pick the kind you're in the mood for.",
         "Decide before you start whether you plan to sleep afterwards."),
        (("What's a good scary movie for someone new to horror?",
          "Start with atmospheric horror or a supernatural thriller rather than extreme gore. Slow dread is easier to handle than constant shocks, and it still delivers."),
         ("What should I watch if I want to be scared but not traumatized?",
          "Look for scary movies that are also tagged funny or atmospheric. They keep the tension without leaving you with images you can't shake.")),
    ),
    "intense": PageContent(
        "Intense Movies That Grip You to the End",
        "Intense movies that keep your pulse up: tight thrillers, relentless action and high-stakes dramas, ranked by rating.",
        "Tight thrillers and relentless pacing",
        ("Intense films don't let go: ticking clocks, high stakes, scenes you watch with your shoulders raised. They're short on filler and long on pressure.",
         "Not a background-movie pick. Put the phone away or you'll miss the point where it tightens."),
    ),
    "chill": PageContent(
        "Chill Movies for Easy Evenings",
        "Chill movies for easy evenings: relaxed, undemanding films you can enjoy without effort. Ranked by rating, tagged by mood.",
        "Easy, undemanding evenings",
        ("Chill movies ask very little of you. The plot is easy to follow, the characters are good company and nobody is going to shout at you. Ideal after a long day.",
         "They're also the right pick when you're sharing the couch and nobody can agree."),
    ),
    "nostalgic": PageContent(
        "Nostalgic Movies That Take You Back",
        "Nostalgic movies that bring back childhood and simpler times: classics, coming-of-age stories and family favorites. Ranked by rating.",
        "Childhood favorites and coming-of-age stories",
        ("Nostalgia is half the film and half what you bring to it. These are older favorites, coming-of-age stories and family classics that tend to take people back to a specific time and place.",
         "Rewatching beats discovering here. If you've seen them before, they usually hold up."),
    ),
    "mind-bending": PageContent(
        "Mind-Bending Movies That Mess With Reality",
        "Mind-bending movies that twist time, memory and reality: puzzle plots and endings worth rewatching, ranked by rating.",
        "Twisty plots that bend time and reality",
        ("These films play with time, memory or what's real, and they reward attention. Expect structures that fold back on themselves and endings that send you straight to the internet to compare theories.",
         "Watch them awake and without distractions. They're less fun if you lose the thread."),
    ),
}

GENRES: dict[str, PageContent] = {
    "drama": PageContent(
        "Best Drama Movies to Watch Right Now",
        "Drama movies built on characters and consequences: family stories, personal struggles and turning points, ranked by rating.",
        "Character-driven stories with real stakes",
        ("Drama is the broadest genre and the one many people end up loving most. These films are built on characters, choices and consequences rather than spectacle.",
         "The mood tags on each card help narrow it down: a sad drama and a thought-provoking one feel very different on a Tuesday night."),
    ),
    "comedy": PageContent(
        "Best Comedy Movies to Watch Tonight",
        "Comedy movies from warm rom-coms to dry satire, ranked by rating, with runtime and mood tags to help you pick.",
        "From warm rom-coms to dry satire",
        ("Comedy ranges from slapstick to deadpan, so use the mood tags: funny for pure laughs, happy for warmth, chill for background company.",
         "Ratings here come from many viewers, which smooths out the personal taste problem a little."),
    ),
    "horror": PageContent(
        "Best Horror Movies, From Slow Dread to Jump Scares",
        "Horror movies ranked by rating: supernatural chills, slashers and psychological dread, with mood tags to match your tolerance.",
        "Supernatural chills and psychological dread",
        ("Horror is a wide field: haunted houses, creature features, psychological dread, folk horror. A film's mood tags, scary, dark, atmospheric, tell you more about the experience than the genre label alone.",
         "New to horror? Start with the highest rated and work toward the stranger end."),
    ),
    "thriller": PageContent(
        "Best Thriller Movies That Keep You Guessing",
        "Thriller movies with tension that builds: conspiracies, chases and psychological games, ranked by rating.",
        "Conspiracies, chases and psychological games",
        ("A good thriller makes you lean forward. These range from cold, procedural tension to full-speed chases, and most are built around a question you can't stop asking.",
         "Avoid reading plot summaries first. The less you know, the better they work."),
    ),
    "sci-fi": PageContent(
        "Best Sci-Fi Movies: Space, Futures and Big Ideas",
        "Sci-fi movies ranked by rating: space epics, near-future dystopias and big ideas, with mood tags like atmospheric and mind-bending.",
        "Space epics, dystopias and big ideas",
        ("Science fiction asks 'what if' on a large scale: what if we leave, what if machines think, what if time isn't linear. Some of these are spectacle, others are quiet and philosophical.",
         "Look at the mood tags: atmospheric and thought-provoking sci-fi is a different evening from an action-led one."),
    ),
    "romance": PageContent(
        "Best Romance Movies for Every Kind of Love Story",
        "Romance movies ranked by rating: slow-burn love stories, comedies and bittersweet endings, with mood tags to find your tone.",
        "Slow burns, rom-coms and bittersweet endings",
        ("Romance isn't one mood. Some of these are light and funny, some ache. The mood tags separate the cozy date-night picks from the ones you'll think about for a week.",),
    ),
    "action": PageContent(
        "Best Action Movies With Real Momentum",
        "Action movies ranked by rating: fights, chases and big set pieces, plus mood tags to separate the smart ones from the loud ones.",
        "Fights, chases and big set pieces",
        ("Action works when the stakes feel real and the set pieces have a point. Use the intense tag for relentless pacing, and the thought-provoking tag for the ones that also have something to say.",),
    ),
    "adventure": PageContent(
        "Best Adventure Movies for Escaping Your Couch",
        "Adventure movies ranked by rating: quests, journeys and far-away places, from family favorites to epic expeditions.",
        "Quests, journeys and far-away places",
        ("Adventures are about going somewhere: across a continent, into space, down a river. They're also a safe bet when you're choosing for a mixed group.",),
    ),
    "mystery": PageContent(
        "Best Mystery Movies for Armchair Detectives",
        "Mystery movies ranked by rating: whodunits, slow-burn puzzles and atmospheric investigations.",
        "Whodunits and slow-burn puzzles",
        ("Mysteries reward attention. Some are classic whodunits, some are more interested in mood than in the answer. Pair them with the atmospheric tag for a late night.",),
    ),
    "crime": PageContent(
        "Best Crime Movies: Heists, Gangsters and Investigations",
        "Crime movies ranked by rating: heists, gangster stories and gritty investigations with mood tags like dark and intense.",
        "Heists, gangsters and gritty investigations",
        ("Crime films are about what people do when the rules stop applying: heists that go sideways, loyalties that don't hold, detectives who get too close.",),
    ),
    "fantasy": PageContent(
        "Best Fantasy Movies to Lose Yourself In",
        "Fantasy movies ranked by rating: magic, mythical worlds and epic quests, from cozy to dark.",
        "Magic, myth and invented worlds",
        ("Fantasy builds a world and invites you to live in it for a while. Cozy fantasy and dark fantasy share a genre label but little else, so check the mood tags.",),
    ),
    "animation": PageContent(
        "Best Animated Movies for All Ages",
        "Animated movies ranked by rating: family favorites, art-house animation and stories that aren't just for kids.",
        "Family favorites and animation for adults",
        ("Animation is a medium, not a genre for kids, and the range is wide: playful family films, melancholy art-house features, lavish fantasy.",),
    ),
    "documentary": PageContent(
        "Best Documentary Movies Worth Your Evening",
        "Documentary movies ranked by rating: true stories, nature, music and investigations with mood tags like thought-provoking.",
        "True stories that stay with you",
        ("Documentaries are the easiest way to spend two hours learning something. Look for the thought-provoking tag, and expect to want to talk about them afterwards.",),
    ),
}

HOME_MOOD_TILES = [
    ("Sad movies", "sad"), ("Romantic movies", "romantic"), ("Movies for late nights", "atmospheric"),
    ("Feel-good movies", "happy"), ("Mind-bending movies", "mind-bending"),
    ("Scary movies", "scary"), ("Movies when you're lonely", "lonely"),
]


def mood_content(slug: str, name: str) -> PageContent:
    return MOODS.get(slug) or PageContent(
        f"Best {name} Movies", f"{name} movies ranked by rating, with runtime, genres and mood tags.", "")


def genre_content(slug: str, name: str) -> PageContent:
    return GENRES.get(slug) or PageContent(
        f"Best {name} Movies", f"{name} movies ranked by rating, with runtime and mood tags.", "")
