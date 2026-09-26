"""Ashen Oath: a text-led endless dungeon expedition built with Tkinter."""

from __future__ import annotations

import random
import json
import time
import os
import tkinter as tk
from dataclasses import replace
from pathlib import Path
from tkinter import font
import webbrowser

from game_data import (
    ABILITY_TEXT,
    ACHIEVEMENTS,
    ALLY_BLESSINGS,
    ALLY_QUOTES,
    ALLY_VISITORS,
    BASE_STATS,
    BOSSES,
    CAMPAIGN_THEMES,
    BOSS_QUOTES,
    ENEMY_QUOTES,
    EQUIPMENT_SLOTS,
    ITEM_AFFIXES,
    ITEM_TEMPLATES,
    MAP_NODES,
    MAX_MANA,
    NORMAL_ENEMIES,
    POTION,
    STARTING_ITEMS,
    SPELLS,
    STATUS_EFFECTS,
    EnemyDefinition,
    ItemDefinition,
    StatModifiers,
)


BG = "#100c13"
PANEL = "#1b1520"
TEXT = "#eee5dc"
MUTED = "#a497a5"
RED = "#df5b5b"
GOLD = "#e6a84e"
TEAL = "#67c2b1"
PURPLE = "#b38ae0"
KOFI_URL = "https://ko-fi.com/martinmartinezgarcia"


class DungeonGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ASHEN OATH — La Hondonada")
        self.root.geometry("1080x760")
        self.root.minsize(900, 650)
        self.root.configure(bg=BG)
        self.rng = random.Random()
        self.music_enabled = True
        self.music_context = "ambient"
        self.music_track_playing: str | None = None
        self.music_generation = 0
        self._init_audio()
        self._make_fonts()
        self.main_menu()

    def _init_audio(self) -> None:
        """Prepare optional MP3 playback; the game still works without pygame."""
        self.audio = None
        audio_dir = Path(__file__).parent / "Audio"
        self.music_tracks = {
            "menu": audio_dir / "Hogar_de_piedra_y_luz.mp3",
            "ambient": audio_dir / "A_Stillness_Held.mp3",
            "boss": audio_dir / "2222222AStillnessHeldmp3cutnet.mp3",
            "ally": audio_dir / "33333333333333Hogardepiedrayluzmp3cutnet.mp3",
        }
        try:
            import pygame

            if self.music_tracks["ambient"].exists():
                pygame.mixer.init()
                self.audio = pygame
        except Exception:
            self.audio = None

    def _start_music(self) -> None:
        if not self.audio or not self.music_enabled:
            return
        path = self.music_tracks.get(self.music_context)
        if self.music_context == "boss" and (not path or not path.exists()):
            path = self.music_tracks["ambient"]
        if not path or not path.exists():
            return
        try:
            if self.music_track_playing == str(path) and self.audio.mixer.music.get_busy():
                return
            self.music_generation += 1
            generation = self.music_generation
            if self.audio.mixer.music.get_busy():
                self.audio.mixer.music.fadeout(650)
                self.root.after(680, lambda: self._load_music_track(path, generation))
            else:
                self._load_music_track(path, generation)
        except self.audio.error:
            self.audio = None

    def _load_music_track(self, path: Path, generation: int) -> None:
        if generation != self.music_generation or not self.audio or not self.music_enabled:
            return
        try:
            self.audio.mixer.music.load(str(path))
            self.audio.mixer.music.set_volume(0.18)
            self.audio.mixer.music.play(-1)
            self.music_track_playing = str(path)
        except self.audio.error:
            self.audio = None

    def _set_music_context(self, context: str) -> None:
        self.music_context = context
        self._start_music()

    def _stop_music(self) -> None:
        self.music_generation += 1
        if self.audio:
            try:
                self.audio.mixer.music.stop()
                self.music_track_playing = None
            except self.audio.error:
                self.audio = None

    def _toggle_music(self) -> None:
        if not self.audio:
            self._log("La música requiere instalar pygame (ver requirements.txt).", "muted")
            return
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self._start_music()
        else:
            self._stop_music()
        self.music_button.configure(text=self._music_button_text())

    def _achievement_path(self) -> Path:
        data_dir = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "ashen-oath"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / "achievements.json"

    def _load_achievements(self) -> None:
        try:
            self.unlocked_achievements = set(json.loads(self._achievement_path().read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError):
            self.unlocked_achievements = set()

    def _unlock_achievement(self, key: str) -> None:
        definition = next((item for item in ACHIEVEMENTS if item.key == key), None)
        if not definition or key in self.unlocked_achievements:
            return
        self.unlocked_achievements.add(key)
        try:
            self._achievement_path().write_text(
                json.dumps(sorted(self.unlocked_achievements), ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            self._log("No se pudo guardar el logro en disco.", "muted")
        self._show_achievement_toast(definition.name, definition.description)

    def _show_achievement_toast(self, title: str, description: str) -> None:
        if not hasattr(self, "root") or not self.root.winfo_exists():
            return
        if self.achievement_toast and self.achievement_toast.winfo_exists():
            self.achievement_toast.destroy()
        toast = tk.Label(self.root, text=f"LOGRO · {title}\n{description}", bg="#443551", fg=TEXT,
                         font=self.small_font, padx=12, pady=8, justify="left")
        toast.place(relx=0.02, rely=0.02, anchor="nw")
        self.achievement_toast = toast
        self.root.after(3600, lambda: toast.destroy() if toast.winfo_exists() else None)

    def _elapsed_text(self) -> str:
        seconds = max(0, int(time.monotonic() - self.started_at))
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def _music_button_text(self) -> str:
        if not self.audio:
            return "♫ Audio no disponible"
        return "♫ Música: " + ("Sí" if self.music_enabled else "No")

    def _make_fonts(self) -> None:
        self.title_font = font.Font(family="TkFixedFont", size=24, weight="bold")
        self.heading_font = font.Font(family="TkFixedFont", size=13, weight="bold")
        self.body_font = font.Font(family="TkFixedFont", size=10)
        self.small_font = font.Font(family="TkFixedFont", size=9)

    def _clear(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()

    def _button(self, parent: tk.Widget, label: str, callback: object, color: str,
                **kwargs: object) -> tk.Button:
        return tk.Button(parent, text=label, command=callback, font=self.body_font, fg=TEXT, bg=color,
                         activebackground="#594459", activeforeground="white", relief="flat",
                         padx=14, pady=10, cursor="hand2", **kwargs)

    def main_menu(self) -> None:
        self._set_music_context("menu")
        self._clear()
        wrapper = tk.Frame(self.root, bg=BG)
        wrapper.pack(fill="both", expand=True)
        tk.Label(wrapper, text="ASHEN OATH", font=self.title_font, fg=PURPLE, bg=BG).pack(pady=(22, 2))
        tk.Label(wrapper, text="UNA EXPEDICIÓN EN LA HONDONADA", font=self.body_font,
                 fg=GOLD, bg=BG).pack()
        self.logo_image = None
        logo_path = Path(__file__).parent / "assets" / "ashen_oath_emblem.png"
        if logo_path.exists():
            try:
                self.logo_image = tk.PhotoImage(file=str(logo_path))
                self.logo_image = self.logo_image.subsample(max(1, self.logo_image.width() // 390))
                tk.Label(wrapper, image=self.logo_image, bg=BG).pack(pady=17)
            except tk.TclError:
                tk.Label(wrapper, text="◈", font=font.Font(size=92), fg=PURPLE, bg=BG).pack(pady=35)
        tk.Label(wrapper, text="La lluvia cae negra. Algo toca una campana bajo tierra.",
                 font=self.body_font, fg=MUTED, bg=BG).pack(pady=(8, 18))
        self._button(wrapper, "NUEVO JUEGO", self.start_run, "#49303a", width=24).pack(pady=5)
        self._button(wrapper, "SALIR", self.root.destroy, "#29232e", width=24).pack(pady=5)
        self._button(wrapper, "☕ INVITAME UN CAFÉ", self._open_kofi, "#29413b", width=24).pack(pady=(12, 5))

    @staticmethod
    def _open_kofi() -> None:
        webbrowser.open_new_tab(KOFI_URL)

    def start_run(self) -> None:
        self._init_run()
        self._build_game_ui()
        self.music_context = "ambient"
        self._start_music()
        self._set_log([
            ("La lluvia cae negra sobre la entrada de La Hondonada.", "muted"),
            ("Kael acepta el trabajo: recuperar el sello antes de que la mina despierte.", ""),
            ("Cada campaña termina en su cuarto encuentro. Las dos primeras peleas son práctica segura.", "gold"),
        ])
        self._path_choice()

    def _init_run(self) -> None:
        self.hp = 86
        self.max_hp = 86
        self.mana = MAX_MANA
        self.max_mana = MAX_MANA
        self.ward = False
        self.started_at = time.monotonic()
        self.node_choices = {}
        self.visited_nodes = []
        self.selected_node = None
        self.in_ally_refuge = False
        self._load_achievements()
        self.achievement_toast = None
        self.campaign = 1
        self.encounter = 0
        self.campaign_bonus_attack = 0
        self.guard = False
        self.enemy_guard = False
        self.enemy_pattern_index = 0
        self.statuses: dict[str, int] = {}
        self.enemy_statuses: dict[str, int] = {}
        self.active_blessings = []
        self.equipped: dict[str, ItemDefinition | None] = dict(zip(EQUIPMENT_SLOTS, STARTING_ITEMS))
        self.inventory: list[ItemDefinition] = [POTION]
        self.potions = 1
        self.pending_loot: list[ItemDefinition] = []
        self.after_loot_action = "continue"
        self.in_combat = False

    def _build_game_ui(self) -> None:
        self._clear()
        header = tk.Frame(self.root, bg=BG, padx=20, pady=10)
        header.pack(fill="x")
        self.brand_label = tk.Label(header, text="ASHEN OATH", font=self.heading_font, fg=PURPLE, bg=BG)
        self.brand_label.pack(side="left")
        self.room_label = tk.Label(header, text="", font=self.body_font, fg=GOLD, bg=BG)
        self.room_label.pack(side="right")
        self.music_button = self._button(header, self._music_button_text(), self._toggle_music, "#29232e")
        self.music_button.pack(side="right", padx=(0, 14))

        body = tk.Frame(self.root, bg=BG, padx=16)
        body.pack(fill="both", expand=True)
        self.left = tk.Frame(body, bg=BG)
        self.left.pack(side="left", fill="both", expand=True)
        self.right_outer = tk.Frame(body, bg=PANEL, width=300,
                                    highlightthickness=1, highlightbackground="#493349")
        self.right_outer.pack(side="right", fill="y", padx=(12, 0))
        self.right_outer.pack_propagate(False)
        self.right_canvas = tk.Canvas(self.right_outer, bg=PANEL, highlightthickness=0, width=280)
        self.right_scrollbar = tk.Scrollbar(self.right_outer, orient="vertical", command=self.right_canvas.yview)
        self.right_canvas.configure(yscrollcommand=self.right_scrollbar.set)
        self.right_scrollbar.pack(side="right", fill="y")
        self.right_canvas.pack(side="left", fill="both", expand=True)
        self.right = tk.Frame(self.right_canvas, bg=PANEL, padx=14, pady=14)
        self.right_window = self.right_canvas.create_window((0, 0), window=self.right, anchor="nw")
        self.right.bind("<Configure>", lambda _e: self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all")))
        self.right_canvas.bind("<Configure>", lambda e: self.right_canvas.itemconfigure(self.right_window, width=e.width))
        self.right_canvas.bind_all("<MouseWheel>", self._scroll_right_panel)
        self.right_canvas.bind_all("<Button-4>", lambda _e: self.right_canvas.yview_scroll(-1, "units"))
        self.right_canvas.bind_all("<Button-5>", lambda _e: self.right_canvas.yview_scroll(1, "units"))

        self.scene = tk.Frame(self.left, bg=PANEL, padx=18, pady=16,
                              highlightthickness=1, highlightbackground="#493349")
        self.scene.pack(fill="both", expand=True)
        self.enemy_title = tk.Label(self.scene, text="", font=self.heading_font, fg=RED, bg=PANEL)
        self.enemy_title.pack(anchor="w")
        self.enemy_desc_label = tk.Label(self.scene, text="", font=self.body_font, fg=MUTED,
                                          bg=PANEL, wraplength=690, justify="left")
        self.enemy_desc_label.pack(anchor="w", pady=(5, 12))
        self.enemy_hp_text = tk.Label(self.scene, text="", font=self.body_font, fg=TEXT, bg=PANEL)
        self.enemy_hp_text.pack(anchor="w")
        self.enemy_bar = tk.Canvas(self.scene, height=12, bg="#38262b", highlightthickness=0)
        self.enemy_bar.pack(fill="x", pady=(4, 13))
        self.hero_title = tk.Label(self.scene, text="KAEL · VIGÍA ERRANTE", font=self.heading_font, fg=TEAL, bg=PANEL)
        self.hero_title.pack(anchor="w")
        self.minimap_label = tk.Label(self.scene, text="", font=self.small_font, fg=GOLD, bg=PANEL,
                                      justify="left", anchor="w")
        self.minimap_label.pack(anchor="nw", pady=(4, 0))
        self.hero_hp_text = tk.Label(self.scene, text="", font=self.body_font, fg=TEXT, bg=PANEL)
        self.hero_hp_text.pack(anchor="w", pady=(5, 0))
        self.hero_bar = tk.Canvas(self.scene, height=12, bg="#25352f", highlightthickness=0)
        self.hero_bar.pack(fill="x", pady=(4, 4))
        self.hero_resource = tk.Label(self.scene, text="", font=self.small_font, fg=GOLD, bg=PANEL)
        self.hero_resource.pack(anchor="w")
        self.hero_mana_bar = tk.Canvas(self.scene, height=8, bg="#243149", highlightthickness=0)
        self.hero_mana_bar.pack(fill="x", pady=(4, 0))

        self.log_box = tk.Text(self.left, height=7, bg="#120e16", fg=TEXT, insertbackground=TEXT,
                               relief="flat", wrap="word", padx=12, pady=8, font=self.small_font,
                               state="disabled")
        self.log_box.pack(fill="x", pady=(9, 6))
        for tag, color in (("danger", RED), ("good", TEAL), ("gold", GOLD), ("muted", MUTED)):
            self.log_box.tag_configure(tag, foreground=color)
        self.actions = tk.Frame(self.left, bg=BG)
        self.actions.pack(fill="x", pady=(0, 8))

        tk.Label(self.right, text="CAMPAÑA", font=self.heading_font, fg=GOLD, bg=PANEL).pack(anchor="w")
        self.campaign_label = tk.Label(self.right, text="", font=self.small_font, fg=MUTED, bg=PANEL,
                                       justify="left", anchor="w")
        self.campaign_label.pack(fill="x", pady=(4, 10))
        tk.Label(self.right, text="ESTADÍSTICAS", font=self.heading_font, fg=TEAL, bg=PANEL).pack(anchor="w")
        self.stats_label = tk.Label(self.right, text="", font=self.small_font, fg=TEXT, bg=PANEL,
                                    justify="left", anchor="w")
        self.stats_label.pack(fill="x", anchor="w", pady=(5, 10))
        tk.Label(self.right,
                 text="Ataque: daño · Defensa: mitiga\nVelocidad: esquiva · Fuego: daño/quemadura\nDuplicación: botín extra",
                 font=self.small_font, fg=MUTED, bg=PANEL, justify="left", wraplength=245).pack(anchor="w", pady=(0, 8))
        tk.Frame(self.right, bg="#493349", height=1).pack(fill="x", pady=(0, 8))
        self.equipment_label = tk.Label(self.right, text="", font=self.small_font, fg=GOLD, bg=PANEL,
                                        justify="left", anchor="nw", wraplength=245)
        self.equipment_label.pack(fill="x", anchor="nw", pady=(0, 8))
        tk.Frame(self.right, bg="#493349", height=1).pack(fill="x", pady=(0, 8))
        tk.Label(self.right, text="MOCHILA", font=self.heading_font, fg=GOLD, bg=PANEL).pack(anchor="w")
        self.bag_item_detail = tk.Label(self.right,
                                        text="Equipo guardado: efectos ×1; equipado: ×2. Seleccioná una pieza para equiparla fuera del combate.",
                                        font=self.small_font, fg=MUTED, bg=PANEL, wraplength=245,
                                        justify="left", anchor="w", height=3)
        self.bag_item_detail.pack(fill="x", pady=(4, 5))
        self.equip_bag_button = self._button(self.right, "⇧ EQUIPAR SELECCIÓN · EFECTO ×2",
                                             self._equip_inventory_item, "#29413b", state=tk.DISABLED)
        self.equip_bag_button.pack(fill="x", pady=(0, 4))
        inventory_frame = tk.Frame(self.right, bg=PANEL, height=150)
        inventory_frame.pack(fill="x", anchor="nw", pady=(0, 0))
        inventory_frame.pack_propagate(False)
        inventory_scroll = tk.Scrollbar(inventory_frame)
        inventory_scroll.pack(side="right", fill="y")
        self.inventory_list = tk.Listbox(inventory_frame, height=5, bg=PANEL, fg=TEXT,
                                         font=self.small_font, relief="flat", activestyle="none",
                                         selectbackground="#594459", selectforeground="white",
                                         exportselection=False, yscrollcommand=inventory_scroll.set)
        self.inventory_list.pack(side="left", fill="both", expand=True)
        self.inventory_list.bind("<<ListboxSelect>>", self._on_inventory_select)
        inventory_scroll.configure(command=self.inventory_list.yview)
        self._capture_theme_widgets()
        self._refresh()
        self._update_clock_display()

    def _scroll_right_panel(self, event: tk.Event) -> None:
        try:
            if self.right_outer.winfo_exists():
                amount = -int(event.delta / 120) if event.delta else 1
                amount = max(-3, min(3, amount))
                self.right_canvas.yview_scroll(amount, "units")
        except tk.TclError:
            return

    def _update_clock_display(self) -> None:
        try:
            if not self.root.winfo_exists() or not hasattr(self, "hero_resource") or not self.hero_resource.winfo_exists():
                return
            status_text = self._status_summary(self.statuses)
            self.hero_resource.configure(text=f"MANÁ {self.mana}/{self.max_mana}   ·   {self._elapsed_text()} de expedición"
                                          + (f"   ·   {status_text}" if status_text else ""))
            self.campaign_label.configure(text=f"{CAMPAIGN_THEMES[(self.campaign - 1) % len(CAMPAIGN_THEMES)].name}"
                                              f"\nCampaña {self.campaign}\nEncuentro {self.encounter}/4"
                                              f"\nTiempo {self._elapsed_text()}")
            self.root.after(1000, self._update_clock_display)
        except tk.TclError:
            return

    def _set_log(self, lines: list[tuple[str, str]]) -> None:
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        for text, tag in lines:
            self.log_box.insert("end", text + "\n", tag)
        self.log_box.configure(state="disabled")

    def _log(self, text: str, tag: str = "") -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _buttons(self, options: list[tuple[str, object, str]]) -> None:
        for child in self.actions.winfo_children():
            child.destroy()
        for index, (label, callback, accent) in enumerate(options):
            self._button(self.actions, label, callback, accent).grid(row=index // 2, column=index % 2,
                                                                     sticky="ew", padx=3, pady=3)
        for col in range(2):
            self.actions.grid_columnconfigure(col, weight=1)

    def _capture_theme_widgets(self) -> None:
        base_roles = {BG: "background", PANEL: "panel", "#120e16": "log"}
        self.theme_roles: dict[tk.Widget, str] = {}
        pending = list(self.root.winfo_children())
        while pending:
            widget = pending.pop()
            pending.extend(widget.winfo_children())
            try:
                role = base_roles.get(str(widget.cget("bg")))
            except tk.TclError:
                role = None
            if role:
                self.theme_roles[widget] = role
        self.theme_roles[self.enemy_bar] = "enemy_bar"
        self.theme_roles[self.hero_bar] = "hero_bar"
        self.theme_roles[self.hero_mana_bar] = "mana_bar"

    def _apply_campaign_theme(self) -> None:
        theme = CAMPAIGN_THEMES[(self.campaign - 1) % len(CAMPAIGN_THEMES)]
        colors = {"background": theme.background, "panel": theme.panel, "log": theme.log_panel,
                  "enemy_bar": "#38262b", "hero_bar": "#25352f", "mana_bar": "#243149"}
        self.root.configure(bg=theme.background)
        for widget, role in self.theme_roles.items():
            try:
                widget.configure(bg=colors[role])
            except tk.TclError:
                continue
        self.scene.configure(highlightbackground=theme.border)
        self.right.configure(highlightbackground=theme.border)
        self.room_label.configure(fg=theme.accent)
        self.brand_label.configure(fg=theme.accent)
        self.current_theme = theme

    def _on_inventory_select(self, _event: object = None) -> None:
        selection = self.inventory_list.curselection()
        if not selection:
            self.bag_item_detail.configure(text="Seleccioná un objeto para ver sus efectos.")
            self.equip_bag_button.configure(state=tk.DISABLED)
            return
        item = self.inventory[selection[0]]
        if item.consumable:
            detail = f"{item.name}: {item.describe()}\nSe usa durante el combate con la acción de botiquín."
            can_equip = False
        else:
            equipped = self.equipped[item.slot]
            replacement = f"Activo ahora: {equipped.name} ({equipped.describe()})" if equipped else "Espacio vacío."
            detail = f"{item.slot}: {item.name} · Mochila ×1 / equipado ×2\n{item.describe()}\n{replacement}"
            can_equip = not self.in_combat
            if not can_equip:
                detail += "\nEl equipo se cambia entre combates."
        self.bag_item_detail.configure(text=detail)
        self.equip_bag_button.configure(state=tk.NORMAL if can_equip else tk.DISABLED)

    def _equip_inventory_item(self) -> None:
        selection = self.inventory_list.curselection()
        if not selection or self.in_combat:
            return
        item = self.inventory[selection[0]]
        if item.consumable:
            return
        self.inventory.pop(selection[0])
        old_item = self.equipped.get(item.slot)
        if old_item:
            self.inventory.append(old_item)
        self.equipped[item.slot] = item
        self._log(f"Equipado desde la mochila: {item.name} ({item.describe()}).", "good")
        self._refresh()

    @staticmethod
    def _bar(canvas: tk.Canvas, current: int, maximum: int, color: str) -> None:
        canvas.delete("all")
        width = max(canvas.winfo_width(), 250)
        canvas.create_rectangle(0, 0, width, 12, fill="#38262b" if color == RED else "#25352f", outline="")
        canvas.create_rectangle(0, 0, width * max(0, current) / maximum, 12, fill=color, outline="")

    def _total_stats(self) -> StatModifiers:
        total = BASE_STATS + StatModifiers(attack=self.campaign_bonus_attack)
        for item in self.inventory:
            if not item.consumable:
                total = total + item.modifiers
        for item in self.equipped.values():
            if item:
                total = total + item.modifiers + item.modifiers
        for blessing in self.active_blessings:
            total = total + blessing.modifiers
        return total

    @staticmethod
    def _signed(value: int) -> str:
        return f"{value:+d}"

    def _refresh(self) -> None:
        if not hasattr(self, "enemy_hp_text"):
            return
        stats = self._total_stats()
        if hasattr(self, "enemy_max_hp"):
            self.enemy_hp_text.configure(text=f"VITALIDAD   {self.enemy_hp:>3}/{self.enemy_max_hp}")
        status_text = self._status_summary(self.statuses)
        self.hero_hp_text.configure(
            text=f"VITALIDAD   {self.hp:>3}/{self.max_hp}    ·    BOTIQUÍN {self.potions}"
                 + (f"    ·    {status_text}" if status_text else ""))
        self.max_mana = max(1, MAX_MANA + stats.mana)
        self.mana = min(self.mana, self.max_mana)
        self.hero_resource.configure(text=f"MANÁ {self.mana}/{self.max_mana}   ·   {self._elapsed_text()} de expedición")
        scene = CAMPAIGN_THEMES[(self.campaign - 1) % len(CAMPAIGN_THEMES)]
        self.campaign_label.configure(text=f"{scene.name}\nCampaña {self.campaign}\nEncuentro {self.encounter}/4\nTiempo {self._elapsed_text()}")
        self.stats_label.configure(text=(f"Ataque       {self._signed(stats.attack)}\nDefensa      {self._signed(stats.defense)}\n"
                                         f"Velocidad    {self._signed(stats.speed)}\nFuego        {self._signed(stats.fire)}\n"
                                         f"Duplicación  {stats.duplication}%\nManá máx.    {self.max_mana}\nPotencia mágica {stats.magic_power:+d}"))
        equipment_lines = ["EQUIPO ACTIVO"]
        for slot in EQUIPMENT_SLOTS:
            item = self.equipped.get(slot)
            equipment_lines.append(f"{slot}: {item.name if item else 'vacío'}")
            if item and item.describe():
                equipment_lines.append(f"  {item.describe()}")
        if self.active_blessings:
            equipment_lines.extend(["", "BENDICIONES (hasta el jefe)"])
            equipment_lines.extend(f"• {blessing.name} · {blessing.description}" for blessing in self.active_blessings)
        self.equipment_label.configure(text="\n".join(equipment_lines))
        self.inventory_list.delete(0, tk.END)
        for item in self.inventory:
            marker = "● " if item.consumable else "◇ "
            passive = " · uso" if item.consumable else " · ×1"
            self.inventory_list.insert(tk.END, f"{marker}{item.name} · {item.describe()}{passive}")
        self.bag_item_detail.configure(text="Equipo guardado aporta ×1; equipado aporta ×2. Las penalizaciones también se duplican.")
        self.equip_bag_button.configure(state=tk.DISABLED)
        self._refresh_minimap()
        if hasattr(self, "enemy_bar") and hasattr(self, "enemy_max_hp"):
            self.root.after_idle(lambda: self._bar(self.enemy_bar, self.enemy_hp, self.enemy_max_hp, RED))
            self.root.after_idle(lambda: self._bar(self.hero_bar, self.hp, self.max_hp, TEAL))
            self.root.after_idle(lambda: self._bar_mana(self.hero_mana_bar, self.mana, self.max_mana))

    @staticmethod
    def _bar_mana(canvas: tk.Canvas, current: int, maximum: int) -> None:
        canvas.delete("all")
        width = max(canvas.winfo_width(), 250)
        canvas.create_rectangle(0, 0, width, 8, fill="#243149", outline="")
        canvas.create_rectangle(0, 0, width * max(0, current) / maximum, 8, fill="#789ce8", outline="")

    def _refresh_minimap(self) -> None:
        if not hasattr(self, "minimap_label"):
            return
        if getattr(self, "in_ally_refuge", False):
            self.minimap_label.configure(text=f"REFUGIO · ALIADO · Campaña {self.campaign}")
            return
        progress = []
        for stage in range(1, 4):
            if stage < self.encounter:
                mark = "●" if stage in self.node_choices else "✓"
            elif stage == self.encounter and self.encounter < 4:
                mark = "◇" if stage not in self.node_choices else "●"
            else:
                mark = "○"
            progress.append(f"{mark} {stage}")
        boss = "◆" if self.encounter == 4 else "◇"
        route = self.node_choices.get(self.encounter)
        node_name = self.selected_node.name if self.encounter in self.node_choices and self.selected_node else None
        detail = f"  {node_name} · {route}" if route and node_name else (f"  Ruta: {route}" if route else "")
        self.minimap_label.configure(text=f"RUTA  {' ─ '.join(progress)} ─ {boss} JEFE{detail}")

    @staticmethod
    def _status_summary(statuses: dict[str, int]) -> str:
        return " · ".join(f"{STATUS_EFFECTS[key].name} {turns}" for key, turns in statuses.items() if turns > 0)

    def _scaled_enemy(self, definition: EnemyDefinition) -> EnemyDefinition:
        tier = self.campaign - 1
        hp_growth = 5 if definition.boss else 3
        attack_growth = tier // 2
        pattern = definition.pattern
        if tier >= 2 and tier % 2 == 0 and len(pattern) < 5:
            escalations = ("poison", "weaken", "burn", "guard", "leech", "heavy")
            escalation = next((action for action in escalations if action not in pattern), None)
            if escalation:
                pattern = pattern + (escalation,)
        return replace(definition, hp=definition.hp + tier * hp_growth,
                       attack_min=definition.attack_min + attack_growth,
                       attack_max=definition.attack_max + attack_growth,
                       pattern=pattern)

    def start_fight(self) -> None:
        if self.encounter == 4:
            boss_index = (self.campaign - 1) % len(BOSSES)
            definition = BOSSES[boss_index]
        else:
            definition = self.rng.choice(NORMAL_ENEMIES)
        if self.encounter < 4 and self.encounter in self.node_choices:
            path = self.node_choices[self.encounter]
            definition = self.rng.choice(NORMAL_ENEMIES)
            if path == "Riesgo":
                definition = self.rng.choice(tuple(enemy for enemy in NORMAL_ENEMIES if enemy.attack_max >= 13))
        self.enemy_definition = self._scaled_enemy(definition)
        self.enemy_name = self.enemy_definition.name
        self.enemy_desc = self.enemy_definition.description
        self.enemy_min = self.enemy_definition.attack_min
        self.enemy_max = self.enemy_definition.attack_max
        self.enemy_pattern_index = 0
        self.enemy_guard = False
        self.enemy_statuses = {}
        self.enemy_max_hp = self.enemy_definition.hp
        self.enemy_hp = self.enemy_max_hp
        self.in_combat = True
        self._set_music_context("boss" if self.enemy_definition.boss else "ambient")
        self.room_label.configure(text=f"CAMPAÑA {self.campaign:02d} · ENCUENTRO {self.encounter}/4")
        self._apply_campaign_theme()
        self.enemy_title.configure(text=self.enemy_name, fg=PURPLE if self.enemy_definition.boss else RED)
        self.enemy_desc_label.configure(text=self.enemy_desc)
        self._refresh()
        if self.encounter in self.node_choices and self.selected_node is not None:
            self._log(f"Kael entra en {self.selected_node.name.lower()}.", "muted")
        tutorial = self.campaign == 1 and self.encounter <= 2
        if tutorial:
            self._set_log([(self.rng.choice(ENEMY_QUOTES), "gold"),
                           ("PRÁCTICA PROTEGIDA: Kael no puede morir en estos dos encuentros.", "gold"),
                           ("Observá la intención del enemigo; sus acciones se anuncian antes de ocurrir.", "muted")])
        elif self.enemy_definition.boss:
            self._set_log([("JEFE DE CAMPAÑA. Si cae Kael, termina la expedición.", "danger"),
                           (self.rng.choice(BOSS_QUOTES), "gold"),
                           ("Un jefe cierra cada campaña; vencerlo abre la siguiente.", "muted")])
        else:
            self._set_log([(self.rng.choice(ENEMY_QUOTES), "gold"),
                           ("Un enemigo bloquea el paso. Leé su intención antes de actuar.", "muted")])
        self._refresh()
        self._show_combat_actions()

    def _current_enemy_action(self) -> str:
        return self.enemy_definition.pattern[self.enemy_pattern_index % len(self.enemy_definition.pattern)]

    def _show_combat_actions(self) -> None:
        action = self._current_enemy_action()
        intent = ABILITY_TEXT.get(action, ABILITY_TEXT["strike"])
        if self.enemy_guard:
            intent += " Está protegido: tu próximo golpe pierde fuerza."
        if self.enemy_statuses:
            intent += " Estado: " + self._status_summary(self.enemy_statuses) + "."
        self.enemy_desc_label.configure(text=f"{self.enemy_desc}\n\nINTENCIÓN: {intent}")
        options = [("[1] Atacar", self.attack, "#49303a"),
                   ("[2] Arco de ceniza · 2 maná · 18 daño", lambda: self.cast_spell(0), "#443551"),
                   ("[3] Defender", self.defend, "#29413b")]
        if self.potions:
            options.append((f"[4] Usar botiquín · {self.potions}", self.heal, "#314344"))
        for index, spell in enumerate(SPELLS[1:], start=2):
            effect = "mitad del próximo golpe" if spell.kind == "ward" else f"cura {spell.power} HP"
            options.append((f"[5] {spell.name} · {spell.cost} maná · {effect}",
                            lambda i=index: self.cast_spell(i), "#35435c"))
        self._buttons(options)
        # Disabled spell buttons remain visible so their costs and effects are discoverable.
        for child in self.actions.winfo_children():
            label = str(child.cget("text"))
            if "maná" in label:
                spell = next((spell for spell in SPELLS if spell.name in label), None)
                if spell and self.mana < spell.cost:
                    child.configure(state=tk.DISABLED, disabledforeground="#827b88")

    def _attack_damage(self, base: int) -> int:
        stats = self._total_stats()
        weakened = STATUS_EFFECTS["weaken"].attack_modifier if self.statuses.get("weaken", 0) else 0
        return max(1, base + stats.attack + stats.fire + weakened)

    def attack(self) -> None:
        damage = self._attack_damage(self.rng.randint(13, 19))
        self._hit_enemy(damage, f"Kael golpea: {damage} de daño.")

    def skill(self) -> None:
        self.cast_spell(0)

    def cast_spell(self, index: int) -> None:
        spell = SPELLS[index]
        if self.mana < spell.cost:
            return
        self.mana -= spell.cost
        stats = self._total_stats()
        power = max(0, stats.magic_power)
        self._unlock_achievement("first_spell")
        if spell.kind == "damage":
            damage = max(1, spell.power + stats.fire + power)
            self._log(f"Kael lanza {spell.name}: {damage} de daño mágico.", "gold")
            self._hit_enemy(damage, "", "gold")
        elif spell.kind == "ward":
            self.ward = True
            self._log("Velo de piedra: el próximo golpe se reduce a la mitad.", "good")
            self._enemy_turn()
        elif spell.kind == "heal":
            restored = min(spell.power + power, self.max_hp - self.hp)
            self.hp += restored
            self._log(f"Sutura ígnea: Kael recupera {restored} HP.", "good")
            self._enemy_turn()

    def _hit_enemy(self, damage: int, message: str, tag: str = "") -> None:
        if self.enemy_guard:
            damage = max(1, damage // 2)
            self.enemy_guard = False
            message += " La guardia enemiga absorbe parte del golpe."
        self.enemy_hp = max(0, self.enemy_hp - damage)
        self._log(message, tag)
        stats = self._total_stats()
        burn_chance = min(80, max(0, stats.fire) * 20)
        if self.enemy_hp > 0 and burn_chance and self.rng.randint(1, 100) <= burn_chance:
            self.enemy_statuses["burn"] = 2
            self._log("Las llamas se aferran al enemigo: Quemadura (2 turnos).", "gold")
        if self.enemy_hp <= 0:
            self._enemy_defeated()
            return
        self._enemy_turn()

    def defend(self) -> None:
        self.guard = True
        self._log("Kael levanta el escudo. El próximo golpe hará menos daño.", "good")
        self._enemy_turn()

    def heal(self) -> None:
        if self.potions <= 0:
            return
        self.potions -= 1
        for index, item in enumerate(self.inventory):
            if item.consumable:
                self.inventory.pop(index)
                break
        restored = min(POTION.heal, self.max_hp - self.hp)
        self.hp += restored
        self._log(f"Botiquín: +{restored} de vitalidad.", "good")
        self._enemy_turn()

    def _enemy_turn(self) -> None:
        if self.statuses.get("weaken", 0):
            self.statuses["weaken"] -= 1
            if self.statuses["weaken"] <= 0:
                del self.statuses["weaken"]
        action = self._current_enemy_action()
        if action == "guard":
            self.enemy_guard = True
            self._log(f"{self.enemy_name.capitalize()} se protege; su próximo daño recibido se reduce.", "muted")
        else:
            raw = self.enemy_max if action == "heavy" else self.rng.randint(self.enemy_min, self.enemy_max)
            damage = self._take_player_damage(raw)
            if damage is None:
                return
            if damage and action == "poison":
                self.statuses["poison"] = 2
                self._log("La herida supura: Kael queda Envenenado durante 2 turnos.", "danger")
            elif damage and action == "burn":
                self.statuses["burn"] = 2
                self._log("El aliento abrasador quema a Kael durante 2 turnos.", "danger")
            elif damage and action == "weaken":
                self.statuses["weaken"] = 2
                self._log("El aullido debilita los ataques de Kael durante 2 turnos.", "danger")
            elif action == "leech" and damage:
                healed = min(6, self.enemy_max_hp - self.enemy_hp)
                self.enemy_hp += healed
                if healed:
                    self._log(f"La sanguijuela absorbe vitalidad y recupera {healed} HP.", "danger")
            if damage:
                self._log(f"{self.enemy_name.capitalize()} golpea: Kael recibe {damage} de daño.", "danger")
        self.enemy_pattern_index += 1
        self.guard = False
        if not self._tick_statuses():
            return
        if self.enemy_hp <= 0:
            self._enemy_defeated()
            return
        self._refresh()
        self._show_combat_actions()

    def _take_player_damage(self, raw_damage: int) -> int | None:
        stats = self._total_stats()
        dodge_chance = min(35, max(0, stats.speed * 5))
        if dodge_chance and self.rng.randint(1, 100) <= dodge_chance:
            self._log(f"Kael esquiva gracias a su velocidad ({dodge_chance}% de probabilidad).", "good")
            return 0
        damage = max(1, raw_damage - stats.defense)
        if self.ward:
            damage = max(1, damage // 2)
            self.ward = False
            self._log("El Velo de piedra absorbe parte del golpe.", "good")
        if self.guard:
            damage = max(1, damage // 2)
        self.hp -= damage
        if self.hp <= 0 and self.campaign == 1 and self.encounter <= 2:
            self.hp = 1
            self._log("Kael cae, pero el instructor lo aparta del golpe final. La práctica continúa.", "gold")
            self._refresh()
            return damage
        if self.hp <= 0:
            self.hp = 0
            self._refresh()
            self._defeat()
            return None
        self._refresh()
        return damage

    def _tick_statuses(self) -> bool:
        for key in ("burn", "poison"):
            turns = self.statuses.get(key, 0)
            if turns:
                effect = STATUS_EFFECTS[key]
                self.hp -= effect.damage_per_turn
                self.statuses[key] = turns - 1
                self._log(f"{effect.name} hiere a Kael: {effect.damage_per_turn} de daño.", "danger")
        for key in ("burn", "poison"):
            turns = self.enemy_statuses.get(key, 0)
            if turns:
                effect = STATUS_EFFECTS[key]
                self.enemy_hp -= effect.damage_per_turn
                self.enemy_statuses[key] = turns - 1
                self._log(f"{effect.name} hiere a {self.enemy_name.lower()}: {effect.damage_per_turn} de daño.", "gold")
        for key in tuple(self.statuses):
            if self.statuses[key] <= 0:
                del self.statuses[key]
        for key in tuple(self.enemy_statuses):
            if self.enemy_statuses[key] <= 0:
                del self.enemy_statuses[key]
        if self.hp <= 0:
            if self.campaign == 1 and self.encounter <= 2:
                self.hp = 1
                self._log("El instructor impide el golpe final durante la práctica.", "gold")
            else:
                self.hp = 0
                self._defeat()
                return False
        if self.enemy_hp <= 0:
            self.enemy_hp = 0
        self._refresh()
        return True

    def _generate_loot(self, positive_only: bool = False) -> ItemDefinition:
        base = self.rng.choice(ITEM_TEMPLATES)
        affix, modifiers = self.rng.choice(ITEM_AFFIXES)
        rolled = base.modifiers + modifiers
        if positive_only:
            rolled = StatModifiers(
                attack=max(0, rolled.attack), defense=max(0, rolled.defense),
                speed=max(0, rolled.speed), fire=max(0, rolled.fire),
                duplication=max(0, rolled.duplication),
                mana=max(0, rolled.mana),
                mana_recovery=max(0, rolled.mana_recovery),
                magic_power=max(0, rolled.magic_power),
            )
            if not any((rolled.attack, rolled.defense, rolled.speed, rolled.fire, rolled.duplication,
                        rolled.mana, rolled.mana_recovery, rolled.magic_power)):
                rolled = StatModifiers(attack=1)
        return replace(base, name=f"{base.name} {affix}", modifiers=rolled)

    def _enemy_defeated(self) -> None:
        self.in_combat = False
        if self.enemy_definition.boss:
            self._set_music_context("ambient")
        self._log(f"{self.enemy_name.capitalize()} cae.", "good")
        if self.encounter < 4:
            self.mana = min(self.max_mana, self.mana + max(1, 2 + self._total_stats().mana_recovery))
            self._log("Kael recupera maná al terminar el encuentro.", "good")
        self.pending_loot = [self._generate_loot()]
        stats = self._total_stats()
        if self.rng.randint(1, 100) <= min(75, max(0, stats.duplication)):
            self.pending_loot.append(self._generate_loot())
            self._log("¡El botín se duplicó!", "gold")
        self.after_loot_action = "boss" if self.encounter == 4 else "normal"
        self._next_loot_choice()

    def _next_loot_choice(self) -> None:
        if not self.pending_loot:
            self._after_loot()
            return
        item = self.pending_loot.pop(0)
        self.pending_item = item
        equipped = self.equipped[item.slot]
        current = (f"\nHoy equipado: {equipped.name} ({equipped.describe()} ×2); al reemplazarlo pasa a mochila ×1."
                   if equipped else "\nEl espacio está vacío.")
        self.room_label.configure(text=f"CAMPAÑA {self.campaign:02d} · BOTÍN")
        self.enemy_title.configure(text=f"BOTÍN: {item.name}", fg=GOLD)
        self.enemy_desc_label.configure(text=f"Espacio: {item.slot}\nEfectos: {item.describe()}{current}\n\nEn mochila aporta ×1; equipado aporta ×2, incluidas sus penalizaciones.")
        self.enemy_hp_text.configure(text="Elegí si equiparlo o guardarlo.")
        self.enemy_bar.delete("all")
        self._refresh()
        self._buttons([
            (f"Equipar en {item.slot}", self._equip_pending, "#29413b"),
            ("Guardar en la mochila", self._keep_pending, "#443551"),
        ])

    def _equip_pending(self) -> None:
        item = self.pending_item
        old_item = self.equipped[item.slot]
        if old_item:
            self.inventory.append(old_item)
        self.equipped[item.slot] = item
        self._log(f"Equipado: {item.name} ({item.describe()}).", "good")
        self._refresh()
        self._next_loot_choice()

    def _keep_pending(self) -> None:
        self.inventory.append(self.pending_item)
        self._log(f"Guardado: {self.pending_item.name}.", "muted")
        self._refresh()
        self._next_loot_choice()

    def _after_loot(self) -> None:
        if self.after_loot_action == "boss":
            self._campaign_victory()
        elif self.encounter < 3:
            self._path_choice()
        elif self.encounter == 3:
            self._choice_room()
        else:
            next_encounter = self.encounter + 1
            self._buttons([(f"Continuar al encuentro {next_encounter}/4",
                            lambda: self._begin_encounter(next_encounter), "#443551")])

    def _begin_encounter(self, encounter: int) -> None:
        self.encounter = encounter
        self.start_fight()

    def _path_choice(self) -> None:
        next_encounter = self.encounter + 1
        self._refresh_minimap()
        self.room_label.configure(text=f"CAMPAÑA {self.campaign:02d} · RUTA {next_encounter}/3")
        options = self.rng.sample(MAP_NODES, 2)
        self.enemy_title.configure(text="EL CAMINO SE DIVIDE", fg=GOLD)
        self.enemy_desc_label.configure(text="Dos pasos llevan más adentro. Elegí uno; ambos vuelven a unirse antes del jefe.\n\n"
                                        + "\n".join(f"• {node.name}: {node.risk}" for node in options))
        self.enemy_hp_text.configure(text="La ruta cambia el enemigo que Kael encontrará.")
        self.enemy_bar.delete("all")
        self._set_log([("La mazmorra ofrece dos caminos.", "gold")])
        self._buttons([
            (f"{options[0].name}\n{options[0].risk}", lambda node=options[0]: self._choose_path(next_encounter, node, "Encuentro"), "#29413b"),
            (f"{options[1].name}\n{options[1].risk}", lambda node=options[1]: self._choose_path(next_encounter, node, "Riesgo"), "#443551"),
        ])

    def _choose_path(self, encounter: int, node: object, path: str) -> None:
        self.node_choices[encounter] = path
        self.encounter = encounter
        self.selected_node = node
        self.start_fight()

    def _choice_room(self) -> None:
        self.room_label.configure(text=f"CAMPAÑA {self.campaign:02d} · PREPARACIÓN DEL JEFE")
        self.enemy_title.configure(text="EL REFUGIO DE LOS MINEROS", fg=GOLD)
        self.enemy_desc_label.configure(text="Antes de la campana, Kael alcanza a buscar vendas o afilar el arma. Solo hay tiempo para una cosa.")
        self.enemy_hp_text.configure(text="Esta ventaja dura hasta el final de la campaña.")
        self.enemy_bar.delete("all")
        self._set_log([("Elegí una preparación antes del cuarto encuentro.", "gold")])
        self._buttons([("Recuperar 22 HP", self.choose_heal, "#29413b"),
                       ("Filo afilado · Ataque +5", self.choose_edge, "#49303a")])

    def choose_heal(self) -> None:
        restored = min(22, self.max_hp - self.hp)
        self.hp += restored
        self.potions += 1
        self.inventory.append(replace(POTION, name="Botiquín encontrado"))
        self._log(f"Kael recupera {restored} HP y encuentra un botiquín.", "good")
        self._prepare_boss()

    def choose_edge(self) -> None:
        self.campaign_bonus_attack = 5
        self._log("Kael afila la espada: Ataque +5 hasta vencer al jefe.", "gold")
        self._prepare_boss()

    def _prepare_boss(self) -> None:
        self.encounter = 4
        self._refresh()
        self._log("La campana vuelve a sonar. Esta vez, desde muy cerca.", "danger")
        self.root.after(650, self.start_fight)

    def _campaign_victory(self) -> None:
        elapsed = self._elapsed_text()
        self._unlock_achievement("first_boss")
        expired_blessings = [blessing.name for blessing in self.active_blessings]
        self.hp = self.max_hp
        self.statuses.clear()
        self.active_blessings.clear()
        self.campaign_bonus_attack = 0
        self.campaign += 1
        if self.campaign >= 5:
            self._unlock_achievement("five_campaigns")
        self.encounter = 0
        self.mana = self.max_mana
        self.node_choices = {}
        self.visited_nodes = []
        self.selected_node = None
        self.in_ally_refuge = False
        self._apply_campaign_theme()
        self._refresh()
        self.room_label.configure(text=f"CAMPAÑA {self.campaign - 1:02d} COMPLETADA")
        self.enemy_title.configure(text="EL SIGUIENTE SELLO SE ABRE", fg=GOLD)
        self.enemy_desc_label.configure(text=f"Kael recupera toda su vitalidad. La expedición continúa hacia la campaña {self.campaign}.")
        self.enemy_hp_text.configure(text="La Hondonada cambia de forma alrededor del siguiente guardián.")
        self.enemy_bar.delete("all")
        lines = [("JEFE DERROTADO · CAMPAÑA SUPERADA", "gold"),
                 (f"Vitalidad restaurada: {self.hp}/{self.max_hp}.", "good")]
        if expired_blessings:
            lines.append(("Las bendiciones se disipan: " + ", ".join(expired_blessings) + ".", "muted"))
        lines.append((f"Un aliado llegó antes de la campaña {self.campaign}.", "muted"))
        self._set_log(lines)
        self._log(f"Tiempo al superar el jefe: {elapsed}.", "muted")
        self._show_ally()

    def _show_ally(self) -> None:
        self.in_combat = False
        self.in_ally_refuge = True
        self._set_music_context("ally")
        visitor, greeting = self.rng.choice(ALLY_VISITORS)
        self.enemy_title.configure(text=visitor.upper(), fg=TEAL)
        self.enemy_desc_label.configure(text=f"{greeting}\n\n«{self.rng.choice(ALLY_QUOTES)}»\n\nTe ofrece tres regalos al azar. Elegí uno para la campaña siguiente.")
        self.enemy_hp_text.configure(text="Un favor; no hace falta pelear ni pagar.")
        self.enemy_bar.delete("all")
        self.ally_offers = [
            {"kind": "blessing", "value": blessing}
            for blessing in ALLY_BLESSINGS
        ]
        self.ally_offers.extend([
            {"kind": "item", "value": self._generate_loot(positive_only=True)},
            {"kind": "supplies", "value": 2},
        ])
        self.ally_offers = self.rng.sample(self.ally_offers, 3)
        options = []
        for index, offer in enumerate(self.ally_offers, start=1):
            if offer["kind"] == "blessing":
                gift = offer["value"]
                label = f"[{index}] {gift.name}\n{gift.description}"
            elif offer["kind"] == "item":
                gift = offer["value"]
                label = f"[{index}] {gift.name}\nMochila ×1: {gift.describe()}"
            else:
                label = f"[{index}] Dos botiquines\nCura 30 HP cada uno"
            options.append((label, lambda i=index - 1: self._choose_ally_gift(i), "#29413b"))
        self._refresh()
        self._buttons(options)

    def _choose_ally_gift(self, index: int) -> None:
        offer = self.ally_offers[index]
        self._unlock_achievement("first_ally")
        if offer["kind"] == "blessing":
            gift = offer["value"]
            self.active_blessings.append(gift)
            message = f"{gift.name}: {gift.description}"
        elif offer["kind"] == "item":
            gift = offer["value"]
            self.inventory.append(gift)
            message = f"{gift.name} se guarda en la mochila y aporta sus efectos ×1."
        else:
            for _ in range(offer["value"]):
                self.inventory.append(replace(POTION, name="Botiquín de Nim"))
                self.potions += 1
            message = "Nim deja dos botiquines en la mochila."
        self._log(message, "good")
        self._refresh()
        self._buttons([(f"Entrar en campaña {self.campaign}", self._enter_campaign, "#443551")])

    def _enter_campaign(self) -> None:
        self.in_ally_refuge = False
        self._set_music_context("ambient")
        self._path_choice()

    def _defeat(self) -> None:
        self.in_combat = False
        self.ended_at = self._elapsed_text()
        self._set_music_context("ambient")
        self.room_label.configure(text="EXPEDICIÓN INTERRUMPIDA")
        self.enemy_title.configure(text="KAEL HA CAÍDO", fg=RED)
        self.enemy_desc_label.configure(text="La Hondonada guarda silencio. Luego, la lluvia vuelve a caer.")
        self._set_log([(f"La expedición duró {self.ended_at}.", "muted"),
                       ("La expedición terminó. Las campañas y el botín se reiniciarán al volver a intentarlo.", "danger")])
        self._buttons([("Volver al menú", self.main_menu, "#29232e"),
                       ("Reintentar desde cero", self.start_run, "#49303a")])


def main() -> None:
    root = tk.Tk()
    DungeonGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
