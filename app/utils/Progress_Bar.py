import sys
import time

def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()
        
        import time

for i in range(101):
    print_progress_bar(i, 100, prefix="Progress", suffix="Complete", length=40)
    time.sleep(0.05)
    
    
     