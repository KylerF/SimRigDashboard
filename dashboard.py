import threading
import pygame

import subscriber

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

def run():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill("blue")

        # Show active driver data
        active_driver_data = subscriber.data['active_driver']
        name = active_driver_data['name']
        nickname = active_driver_data['nickname']

        font = pygame.font.SysFont('Arial', 24)
        name_text = font.render(f'Name: {name if name else "Loading..."}', True, 'white')
        nickname_text = font.render(f'Nickname: {nickname if nickname else "Loading..."}', True, 'white')
        screen.blit(name_text, (10, 10))
        screen.blit(nickname_text, (10, 40))

        # Show iRacing data
        iracing_data = subscriber.data['iracing']
        speed = iracing_data['Speed']
        rpm = iracing_data['RPM']
        gear = iracing_data['Gear']

        font = pygame.font.SysFont('Arial', 24)
        speed_text = font.render(f'Speed: {speed}', True, 'white')
        rpm_text = font.render(f'RPM: {rpm}', True, 'white')
        gear_text = font.render(f'Gear: {gear}', True, 'white')
        screen.blit(speed_text, (10, 100))
        screen.blit(rpm_text, (10, 140))
        screen.blit(gear_text, (10, 180))

        pygame.display.flip()

        clock.tick(60)

if __name__ == "__main__":
    thread = threading.Thread(target=subscriber.start)
    thread.start()

    run()

    thread.join()
