from pygame import Rect
import pgzrun

WIDTH = 1200
HEIGHT = 600
TITLE = "Platformer Game For Kodland"

# Platformları tanımlıyoruz: Her biri hem Rect hem de Actor tutacak
platforms = [
    {"rect": Rect((0, 450), (144, 48)), "actor": Actor("platform", (72, 474)), },
    {"rect": Rect((200, 400), (144, 48)), "actor": Actor("platform", (272, 424))},
    {"rect": Rect((400, 350), (144, 48)), "actor": Actor("platform", (472, 374))},
    {"rect": Rect((600, 300), (144, 48)), "actor": Actor("platform", (672, 324))},
    {"rect": Rect((800, 250), (144, 48)), "actor": Actor("platform", (872, 274))},
    {"rect": Rect((1000, 200), (144, 48)), "actor": Actor("platform", (1072, 224))},
]

# Düşmanı ve düşmana ait animasyonları tanımıyoruz
enemy = Actor("enemy_walk1")
enemy.platform_index = 3
enemy.bottom = platforms[enemy.platform_index]["rect"].top
enemy.speed = 2
enemy.boundary_left = platforms[enemy.platform_index]["rect"].left
enemy.boundary_right = platforms[enemy.platform_index]["rect"].right
enemy_images = ["enemy_walk1", "enemy_walk2"]

player = Actor("hero_idle1")
player.bottomleft = (50, 350)
# Karakter için değişkenler
player.velocity_x = 4
player.velocity_y = 0
player.jumping = False
player.alive = True
player.state = "idle"

# Oyun sonu ödülü için değişkenler
trophy = Actor("end")
last_platform = platforms[-1]
trophy.pos = (last_platform["rect"].right - 30, last_platform["rect"].top - trophy.height / 2)

# Görseller
idle_images = ["hero_idle1", "hero_idle2"]
run_images = ["hero_run1", "hero_run2", "hero_run3"]

# Hesaplamalar için gerekli değişkenler
idle_index = 0
run_index = 0
enemy_index = 0
frame_duration = 0.15
time_since_last_frame = 0

# Global değişkenler
gravity = 1
jump_velocity = -12
over = False
win = False

game_state = "menu"
music_on = True
sound_played = False

start_button = Rect((WIDTH // 2 - 100, 200, 200, 50))
music_button = Rect((WIDTH // 2 - 100, 300, 200, 50))
exit_button = Rect((WIDTH // 2 - 100, 400, 200, 50))

music.play("background_music")
music.set_volume(0.5)
sounds.death.set_volume(0.5)

def draw():
    if game_state == "menu":
        draw_menu()
    else:
        draw_game()

def draw_menu():
    screen.clear()
    screen.fill("darkslateblue")
    screen.draw.text("Ana menu", center=(WIDTH // 2, 100), fontsize=64, color="white")
    screen.draw.filled_rect(start_button, "limegreen")
    screen.draw.text("Oyuna Basla", center=start_button.center, fontsize=32, color="white")
    screen.draw.filled_rect(music_button, "tan")
    screen.draw.text("Muzigi ac/kapat", center=music_button.center, fontsize=32, color="white")
    screen.draw.filled_rect(exit_button, "red")
    screen.draw.text("Cikis yap", center=exit_button.center, fontsize=32, color="white")

def draw_game():
    screen.clear()
    screen.fill("skyblue")
    for platform in platforms:
        platform["actor"].draw()
        # screen.draw.rect(platform["rect"], "red")  # Debug için kullanılabilir
    enemy.draw()
    trophy.draw()

    if player.alive:
        player.draw()

    if over and not win:
        screen.draw.text("Kaybettin!", center=(WIDTH / 2, HEIGHT / 2), fontsize=28)
        screen.draw.text("Tekrar baslamak icin R tusuna bas.", center=(WIDTH / 2, (HEIGHT / 2) + 30), fontsize=20)

    if win:
        music.stop()
        screen.draw.text("Kazandin!", center=(WIDTH / 2, HEIGHT / 2), fontsize=28)


def update(dt):
    global over, time_since_last_frame, win, sound_played

    if game_state == "menu":
        return

    # Sola koşmayla alakalı kısım / çarpışmaları denetliyoruz
    if keyboard.left and player.midleft[0] > 0:
        player.state = "run"
        player.x -= player.velocity_x
        rect_list = [platform["rect"] for platform in platforms]
        index = player.collidelist(rect_list)
        if index != -1:
            object = rect_list[index]
            player.left = object.right

    # Sağa koşmayla alakalı kısım / çarpışmaları denetliyoruz
    elif keyboard.right and player.midright[0] < WIDTH:
        player.state = "run"
        player.x += player.velocity_x
        rect_list = [platform["rect"] for platform in platforms]
        index = player.collidelist(rect_list)
        if index != -1:
            object = rect_list[index]
            player.right = object.left
    else:
        player.state = "idle"
    # yerçekimi
    player.y += player.velocity_y
    player.velocity_y += gravity

    if player.bottom >= HEIGHT:
        player.alive = False
        over = True

    rect_list = [platform["rect"] for platform in platforms]
    index = player.collidelist(rect_list)
    if index != -1:
        object = rect_list[index]
        # aşağı iniyor demek
        if player.velocity_y >= 0:
            player.bottom = object.top
            player.jumping = False
        # yukarı doğru çıkıyor demek
        else:
            player.top = object.bottom
        player.velocity_y = 0

    if player.colliderect(trophy):
        win = True

    time_since_last_frame += dt
    if time_since_last_frame >= frame_duration:
        time_since_last_frame = 0
        toggle_animation()

    move_enemy()

    if player.colliderect(enemy):
        if not sound_played:
            sounds.death.play()
            sound_played = True
        player.alive = False
        over = True

def move_enemy():
    enemy.x += enemy.speed

    if enemy.x <= enemy.boundary_left:
        enemy.x = enemy.boundary_left
        enemy.speed *= -1
    elif enemy.x >= enemy.boundary_right:
        enemy.x = enemy.boundary_right
        enemy.speed *= -1

def toggle_animation():
    global idle_index, run_index, enemy_index
    if player.state == "idle":
        idle_index = (idle_index + 1) % len(idle_images)
        player.image = idle_images[idle_index]
    elif player.state == "run":
        run_index = (run_index + 1) % len(run_images)
        player.image = run_images[run_index]
    enemy_index = (enemy_index + 1) % len(enemy_images)
    enemy.image = enemy_images[enemy_index]

def reset_game():
    global player, enemy, over, win, sound_played

    # Reset player state
    player.bottomleft = (50, 350)
    player.velocity_x = 4
    player.velocity_y = 0
    player.jumping = False
    player.alive = True
    player.state = "idle"

    # Reset enemy state
    enemy.platform_index = 3
    platform = platforms[enemy.platform_index]
    enemy.bottom = platform["rect"].top
    enemy.x = (platform["rect"].left + platform["rect"].right) / 2
    enemy.speed = 2

    # Reset game state
    over = False
    win = False
    sound_played = False

    # Reset trophy position
    last_platform = platforms[-1]
    trophy.pos = (last_platform["rect"].right - 30, last_platform["rect"].top - trophy.height / 2)


def on_key_down(key):
    global game_state, over
    if key == keys.UP and not player.jumping:
        player.image = "hero_jump"
        sounds.jump.play()
        player.velocity_y = jump_velocity
        player.jumping = True
    if key == keys.R:
        if game_state == "playing" and over:
            reset_game()

def on_mouse_down(pos):
    global game_state, music_on
    if game_state == "menu":
        if start_button.collidepoint(pos):
            game_state = "playing"
        elif music_button.collidepoint(pos):
            music_on = not music_on
            if music_on:
                music.play("background_music")
            else:
                music.stop()
        elif exit_button.collidepoint(pos):
            exit()

pgzrun.go()