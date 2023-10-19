no_of_stalls = [2, 3, 20, 30, 100]
no_of_obstacles = [0, 50, 200]
players = ['1 2 3 4 5 6',\
           '1 1 1 2 2 2 3 3 3 4 4 4 5 5 5 6 6 6',\
           '1 1 1 1 1 1 2 2 2 2 2 2 3 3 3 3 3 3 4 4 4 4 4 4 5 5 5 5 5 5 6 6 6 6 6 6 ',
           '1 1 1 1 1 1',
           '2 2 2 2 2 2',
           '3 3 3 3 3 3',
           '4 4 4 4 4 4',
           '5 5 5 5 5 5',
           '6 6 6 6 6 6',
           '1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1',
           '2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2',
           '3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3',
           '4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4',
           '5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5',
           '6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6',
           '1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1',
           '2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2',
           '3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3',
           '4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4',
           '5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5',
           '6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6']

theta = [1, 2, 3]

with open('tournament_1.sh', 'w') as f:
    f.write('')

with open('tournament_2.sh', 'w') as f:
    f.write('')

with open('tournament_3.sh', 'w') as f:
    f.write('')

total = len(no_of_stalls) * len(no_of_obstacles) * len(players) * len(theta)
count = 0
for nv in no_of_stalls:
    for no in no_of_obstacles:
        for p in players:
            for t in theta:
                count += 1
                with open('tournament_1.sh', 'a') as f:
                    f.write('python main.py --gui False -ns ' + str(nv + no) + ' -nv ' + str(nv) + ' -p ' + str(p) + ' --theta ' + str(t) + " --seed 5\n")
                    f.write('cat logs/game_config.txt >> tournament_results.txt\n')
                    f.write('cat logs/result.txt >> tournament_results.txt\n')
                    f.write('echo "run ' + str(count) + '/' + str(total) + '"' + '\n')

for nv in no_of_stalls:
    for no in no_of_obstacles:
        for p in players:
            for t in theta:
                with open('tournament_2.sh', 'a') as f:
                    f.write('python main.py --gui False -ns ' + str(nv + no) + ' -nv ' + str(nv) + ' -p ' + str(p) + ' --theta ' + str(t) + " --seed 10\n")
                    f.write('cat logs/game_config.txt >> tournament_results.txt\n')
                    f.write('cat logs/result.txt >> tournament_results.txt\n')

for nv in no_of_stalls:
    for no in no_of_obstacles:
        for p in players:
            for t in theta:
                with open('tournament_3.sh', 'a') as f:
                    f.write('python main.py --gui False -ns ' + str(nv + no) + ' -nv ' + str(nv) + ' -p ' + str(p) + ' --theta ' + str(t) + " --seed 15\n")
                    f.write('cat logs/game_config.txt >> tournament_results.txt\n')
                    f.write('cat logs/result.txt >> tournament_results.txt\n')
