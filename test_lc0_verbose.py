import subprocess, time
p = subprocess.Popen([r'C:\Users\Admin\Documents\chess_speak_out_loud\engine\lc0.exe', '--weights', r'C:\Users\Admin\Documents\chess_speak_out_loud\engine\791556.pb.gz'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
p.stdin.write('uci\n')
p.stdin.write('setoption name VerboseMoveStats value true\n')
p.stdin.write('position startpos\n')
p.stdin.write('go nodes 1\n')
p.stdin.flush()
time.sleep(2)
p.stdin.write('quit\n')
p.stdin.flush()
stdout, stderr = p.communicate()
for line in stdout.split('\n'):
    if 'info string' in line or 'bestmove' in line:
        print(line.strip())
