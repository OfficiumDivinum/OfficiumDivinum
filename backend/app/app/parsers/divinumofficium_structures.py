"""Structures used by divinumofficium, since Lazslo Kiss rolled his own database and all
kinds of other fun stuff in perl, and we want to be able to parse it without horrendous
amounts of hard coding."""

versions = [
    "Monastic",
    "Tridentine 1570",
    "Tridentine 1910",
    "Divino Afflatu",
    "Reduced 1955",
    "Rubrics 1960",
    "1960 Newcalendar",
]


commands = [
    "Ante",
    "Matutinum",
    "Laudes",
    "Prima",
    "Tertia",
    "Sexta",
    "Nona",
    "Vespera",
    "Completorium",
    "Past",
]


monthnames = [
    "Januarius",
    "Februarius",
    "Martius",
    "Aprilis",
    "Majus",
    "Junius",
    "Julius",
    "Augustus",
    "September",
    "October",
    "November",
    "December",
]  # why do we give up on Latin half way through?!?!


traditional_rank_table = [
    "feria",  # was: none
    "simplex",
    "semiduplex",
    "duplex",
    "duplex majus",
    "duplex ii classis",
    "duplex i classis",
    "duplex i classis",
]

traditional_rank_lookup_table = {
    "feria": 0,
    "simplex": 1,
    "semiduplex": 2,
    "duplex": 3,
    "duplex majus": 4,
    "duplex ii classis": 5,
    "duplex i classis": 6,
    "semiduplex i classis": 2.5,
    "i ordinis": 6,
    "i classis": 6,
}

typo_translations = {
    "I classis Semiduplex": "Semiduplex I classis",
    "Feria privilegiata Duplex I classis": "Feria privilegiata",
    "Duplex 2 class": "Duplex II classis",
    "Semiduplex I class": "Semiduplex I classis",
    "I": "I classis",
}

new_rank_table = [
    "feria",  # was: none
    "commemoratio",
    "iii. classis",
    "iii. classis",
    "iii. classis",
    "ii. classis",
    "i. classis",
    "i. classis",
]

feria_ranks = {
    "feria minor": 0,
    "feria major": 0.5,
    "feria privilegiata": 8,  # outrank everything
    "i classis": 8,  # outrank everything!
    "ii classis": 5,  # same rank as 2nd class feasts, outranking solved in Calendar()
    "iii classis": 2,  # same rank as 3rd class feasts, outranking solve in Calendar()
    "iv classis": 0,
}


rank_table_by_calendar = {"1960": new_rank_table}

latin_feminine_ordinals = [
    "prima",
    "secunda",
    "tertia",
    "quarta",
    "quinta",
    "sexta",
    "septima",
    "octava",
    "nona",
    "decima",
    "undecima",
    "duodecima",
    "tertia decima",
    "quarta decima",
    "quinta decima",
    "sexta decima",
    "septima decima",
    "duodevicesima",
    "undevicesima",
    "vicesima",
    "vicesima prima",
    "vicesima secunda",
    "vicesima tertia",
    "vicesima quarta",
    "vicesima quinta",
    "vicesima sexta",
    "vicesima septima",
    "vicesima octava",
    "vicesima nona",
    "tricesima",
]
