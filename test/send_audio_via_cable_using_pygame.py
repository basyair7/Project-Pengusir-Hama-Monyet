import pygame

pygame.mixer.init()
sound = pygame.mixer.Sound('example.mp3')
playing = sound.play()
while playing.get_busy():
    pygame.time.delay(100)
