"""Content definitions for Ashen Oath, kept separate from the Tk interface."""

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class StatModifiers:
    attack: int = 0
    defense: int = 0
    speed: int = 0
    fire: int = 0
    duplication: int = 0
    mana: int = 0
    mana_recovery: int = 0
    magic_power: int = 0

    def __add__(self, other: "StatModifiers") -> "StatModifiers":
        return StatModifiers(
            self.attack + other.attack,
            self.defense + other.defense,
            self.speed + other.speed,
            self.fire + other.fire,
            self.duplication + other.duplication,
            self.mana + other.mana,
            self.mana_recovery + other.mana_recovery,
            self.magic_power + other.magic_power,
        )


@dataclass(frozen=True)
class ItemDefinition:
    name: str
    slot: str
    modifiers: StatModifiers = field(default_factory=StatModifiers)
    description: str = ""
    consumable: bool = False
    heal: int = 0

    def describe(self) -> str:
        effects = []
        for label, value in (
            ("Ataque", self.modifiers.attack),
            ("Defensa", self.modifiers.defense),
            ("Velocidad", self.modifiers.speed),
            ("Fuego", self.modifiers.fire),
        ):
            if value:
                effects.append(f"{label} {value:+d}")
        if self.modifiers.duplication:
            effects.append(f"Duplicación {self.modifiers.duplication:+d}%")
        if self.modifiers.mana:
            effects.append(f"Maná máximo {self.modifiers.mana:+d}")
        if self.modifiers.mana_recovery:
            effects.append(f"Recuperación de maná {self.modifiers.mana_recovery:+d}")
        if self.modifiers.magic_power:
            effects.append(f"Potencia mágica {self.modifiers.magic_power:+d}")
        if self.heal:
            effects.append(f"Cura {self.heal} HP")
        return " · ".join(effects) or self.description


@dataclass(frozen=True)
class EnemyDefinition:
    name: str
    description: str
    hp: int
    attack_min: int
    attack_max: int
    pattern: tuple[str, ...] = ("strike", "strike")
    boss: bool = False


@dataclass(frozen=True)
class StatusDefinition:
    name: str
    damage_per_turn: int = 0
    attack_modifier: int = 0


@dataclass(frozen=True)
class SceneTheme:
    name: str
    background: str
    panel: str
    log_panel: str
    border: str
    accent: str


@dataclass(frozen=True)
class BlessingDefinition:
    name: str
    description: str
    modifiers: StatModifiers


@dataclass(frozen=True)
class SpellDefinition:
    name: str
    cost: int
    description: str
    kind: str
    power: int


@dataclass(frozen=True)
class MapNode:
    name: str
    risk: str


@dataclass(frozen=True)
class AchievementDefinition:
    key: str
    name: str
    description: str


STATUS_EFFECTS: Mapping[str, StatusDefinition] = {
    "burn": StatusDefinition("Quemadura", damage_per_turn=3),
    "poison": StatusDefinition("Veneno", damage_per_turn=3),
    "weaken": StatusDefinition("Debilitado", attack_modifier=-2),
}

EQUIPMENT_SLOTS = ("Arma", "Armadura", "Amuleto")
BASE_STATS = StatModifiers(speed=1, duplication=10)
MAX_MANA = 6
SPELLS = (
    SpellDefinition("Arco de ceniza", 2, "Inflige 18 de daño mágico; el fuego lo potencia.", "damage", 18),
    SpellDefinition("Velo de piedra", 2, "Reduce a la mitad el próximo golpe recibido.", "ward", 0),
    SpellDefinition("Sutura ígnea", 3, "Recupera 24 de vitalidad.", "heal", 24),
)
MAP_NODES = (
    MapNode("Galería de campanas", "Un guardián protege el paso."),
    MapNode("Pozo de tiza", "La piedra está cubierta de polvo irritante."),
    MapNode("Túnel de raíces", "Algo se mueve bajo el suelo."),
    MapNode("Puente hundido", "El camino cruje bajo cada pisada."),
    MapNode("Cantera ciega", "Un saqueador busca lo que Kael lleva."),
    MapNode("Cámara de brasas", "El calor anuncia una criatura cercana."),
)
ENEMY_QUOTES = (
    "No suelo compartir el camino. Ni la salida.",
    "Tu armadura hace un ruido muy tranquilizador.",
    "La última persona que pasó dejó mejores botas.",
    "Tranquilo. Esto probablemente duela poco.",
)
BOSS_QUOTES = (
    "La campana ya decidió quién se queda.",
    "Cada campaña trae otro voluntario.",
    "Te guardé un sitio bajo las piedras.",
)
ALLY_QUOTES = (
    "Llegaste vivo. Qué forma tan rara de empezar una conversación.",
    "Te traje algo útil. Creo. Lo encontré en una caja sin dueño.",
    "Descansá un momento. Las piedras pueden esperar.",
)
ACHIEVEMENTS = (
    AchievementDefinition("first_boss", "Primera campana", "Derrotá a tu primer jefe."),
    AchievementDefinition("five_campaigns", "Todavía en pie", "Alcanzá la campaña 5."),
    AchievementDefinition("first_spell", "Palabras de fuego", "Lanzá tu primer hechizo."),
    AchievementDefinition("first_ally", "Una mano en la oscuridad", "Recibí ayuda de un aliado."),
)
CAMPAIGN_THEMES = (
    SceneTheme("La Hondonada", "#100c13", "#1b1520", "#120e16", "#493349", "#b38ae0"),
    SceneTheme("Galería de Raíces", "#0d1312", "#17201e", "#101715", "#34504a", "#76c6a9"),
    SceneTheme("Pozo Azul", "#0c1018", "#171c27", "#10141e", "#37485f", "#86b2ed"),
    SceneTheme("Forja Sepultada", "#17100e", "#241a16", "#19110f", "#594033", "#e2a568"),
)

ALLY_BLESSINGS = (
    BlessingDefinition("Paso del cuervo", "Velocidad +2 hasta el próximo jefe.", StatModifiers(speed=2)),
    BlessingDefinition("Piel de cantera", "Defensa +2 hasta el próximo jefe.", StatModifiers(defense=2)),
    BlessingDefinition("Filo prestado", "Ataque +2 hasta el próximo jefe.", StatModifiers(attack=2)),
    BlessingDefinition("Brasa amiga", "Fuego +2 hasta el próximo jefe.", StatModifiers(fire=2)),
    BlessingDefinition("Mano afortunada", "Duplicación +20% hasta el próximo jefe.", StatModifiers(duplication=20)),
)

ALLY_VISITORS = (
    ("Lúa, la rastreadora", "Trae barro fresco en las botas y conoce un atajo entre las galerías."),
    ("Taren, el farolero", "Una luz verde tiembla en su farol. Dice que puede ayudar, por una vez."),
    ("Nim, la boticaria", "Deja su mochila en el suelo y empieza a revisar las heridas de Kael."),
    ("Orvek, el buscador", "Aparece cargando algo que jura haber encontrado y no robado."),
)

STARTING_ITEMS = (
    ItemDefinition("Espada mellada", "Arma", StatModifiers(attack=1), "Una hoja gastada, todavía útil."),
    ItemDefinition("Escudo de tablones", "Armadura", StatModifiers(defense=1), "Madera reforzada con hierro."),
    ItemDefinition("Amuleto de hilo", "Amuleto", description="Un nudo apretado contra la mala suerte."),
)

POTION = ItemDefinition("Botiquín", "Consumible", description="Vendas y tintura amarga.", consumable=True, heal=30)

NORMAL_ENEMIES = (
    EnemyDefinition("SAQUEADOR DE CENIZA", "Un ladrón de las galerías que abre el combate con una embestida.", 38, 7, 12),
    EnemyDefinition("CUERVO DE PIEDRA", "Un ave de alas minerales. Su picada pesada se anuncia con un graznido.", 34, 8, 13, ("strike", "heavy")),
    EnemyDefinition("BRUTO DE MUSGO", "Lento y cubierto de raíces. Levanta una defensa antes de golpear.", 48, 6, 14, ("guard", "heavy", "strike")),
    EnemyDefinition("LARVA DE BRASA", "Una criatura acorazada que calienta su aliento antes de escupir fuego.", 42, 7, 12, ("strike", "burn")),
    EnemyDefinition("HURÓN DE LAS GRIETAS", "Pequeño, rápido y con colmillos manchados de una savia oscura.", 36, 6, 11, ("strike", "poison")),
    EnemyDefinition("PEREGRINO DE VIDRIO", "Su máscara refleja a Kael con un instante de retraso.", 44, 7, 13, ("weaken", "strike")),
    EnemyDefinition("SANGUIJUELA DE TIZA", "Se arrastra por la piedra y se aferra a cualquier herida abierta.", 40, 6, 12, ("strike", "leech")),
    EnemyDefinition("VIGÍA SIN ROSTRO", "Una armadura vacía que protege sus puntos débiles antes de atacar.", 50, 8, 14, ("guard", "strike", "heavy")),
)

BOSSES = (
    EnemyDefinition("EL CAMPANERO HUECO", "Algo antiguo bajo una armadura de mina. Cada campanada anuncia un golpe demoledor.", 82, 13, 20, ("strike", "heavy", "weaken"), True),
    EnemyDefinition("LA VIUDA DE HOLLÍN", "Una criatura envuelta en velos de ceniza. Su aguijón deja veneno que no se ve.", 88, 11, 19, ("poison", "strike", "heavy"), True),
    EnemyDefinition("EL SANTO DE RAÍCES", "Un guardián de madera petrificada que se recompone tras protegerse.", 96, 10, 21, ("guard", "heavy", "leech"), True),
)

ITEM_TEMPLATES = (
    ItemDefinition("Hoja de brasa", "Arma", StatModifiers(attack=4, fire=2, defense=-1), "Arde al rozar el aire."),
    ItemDefinition("Daga del corredor", "Arma", StatModifiers(attack=-1, speed=3), "Ligera como una mala decisión."),
    ItemDefinition("Hachuela de cantera", "Arma", StatModifiers(attack=6, speed=-2), "Golpea fuerte; tarda en volver."),
    ItemDefinition("Malla de minero", "Armadura", StatModifiers(defense=3, speed=-1), "Cadenas toscas, buen trabajo."),
    ItemDefinition("Manto de las grietas", "Armadura", StatModifiers(defense=-1, speed=3), "No detiene el golpe, ayuda a no estar ahí."),
    ItemDefinition("Peto de escoria", "Armadura", StatModifiers(defense=5, attack=-1, speed=-2), "Resistente y nada discreto."),
    ItemDefinition("Dado de cobre", "Amuleto", StatModifiers(duplication=25, defense=-1), "La suerte cobra una pequeña tarifa."),
    ItemDefinition("Ojo de tormenta", "Amuleto", StatModifiers(speed=2, fire=2, defense=-1), "Un brillo frío palpita dentro."),
    ItemDefinition("Medalla de plomo", "Amuleto", StatModifiers(defense=3, speed=-1), "Pesa más de lo que parece."),
    ItemDefinition("Ceniza afortunada", "Amuleto", StatModifiers(attack=2, duplication=10, speed=-1), "Nunca se sabe qué parte trae suerte."),
    ItemDefinition("Cristal de maná", "Amuleto", StatModifiers(mana=1, magic_power=1), "Una reserva pequeña, una chispa más fuerte."),
    ItemDefinition("Brazal de enfoque", "Armadura", StatModifiers(mana_recovery=1, defense=-1), "Ayuda a recuperar el aliento mágico; deja el costado expuesto."),
    ItemDefinition("Anillo de brasas", "Amuleto", StatModifiers(magic_power=2, attack=-1), "La magia prende rápido, la espada pesa menos."),
)

ITEM_AFFIXES = (
    ("del pulso", StatModifiers(speed=1, attack=-1)),
    ("de puño", StatModifiers(attack=2, defense=-1)),
    ("de guardia", StatModifiers(defense=2, speed=-1)),
    ("de chispas", StatModifiers(fire=1, duplication=-5)),
    ("de la suerte", StatModifiers(duplication=10, attack=-1)),
    ("de plomo", StatModifiers(defense=1, speed=-2)),
    ("del manantial", StatModifiers(mana=1, defense=-1)),
    ("del enfoque", StatModifiers(mana_recovery=1, attack=-1)),
    ("de la chispa", StatModifiers(magic_power=1, speed=-1)),
)

ABILITY_TEXT: Mapping[str, str] = {
    "strike": "Ataca con un golpe normal.",
    "heavy": "Prepara un golpe pesado: defenderse reduce mucho el daño.",
    "guard": "Se protege: el próximo golpe de Kael hará menos daño.",
    "poison": "Su mordida puede envenenar a Kael durante dos turnos.",
    "burn": "Acumula calor y puede quemar a Kael durante dos turnos.",
    "weaken": "Su aullido puede debilitar el próximo ataque de Kael.",
    "leech": "Intenta herir a Kael y recuperar parte de su vitalidad.",
}
