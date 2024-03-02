import sys
import time

def animated_loading():
    chars = "/—\\|"
    while True:
        for char in chars:
            sys.stdout.write('\r' + 'Загрузка ' + char)
            time.sleep(.1)
            sys.stdout.flush()

# Пример использования
animated_loading()
print("\nЗагрузка завершена!")