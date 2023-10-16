import argparse
from dodgem_game import DodgemGame

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--no_of_stalls", "-ns", default=100, help="Number of stalls")
    parser.add_argument("--no_to_visit", "-nv", default=50, help="Number of stalls to visit by the players")
    parser.add_argument("--theta", "-theta", default=2, help="Theta value")
    parser.add_argument("--total_time", "-T", default=-1, help="Total time threshold")
    parser.add_argument("--players", "-p", default=['1', '2', '3', '4', '5', '6'], nargs="+", help="List of players space separated")
    parser.add_argument("--seed", "-s", default=2, help="Seed")
    parser.add_argument("--gui", "-g", default="True", help="GUI")
    parser.add_argument("--scale", "-sc", default=10, help="Scale factor")
    parser.add_argument("--interval", "-i", default=100, help="Time in ms after which the next iteration is executed")
    parser.add_argument("--disable_tsp", "-d", default="False", help="Disable or enable the tsp algorithm in simulator")
    args = parser.parse_args()
    dodgem_game = DodgemGame(args)