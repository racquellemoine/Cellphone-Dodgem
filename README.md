# Project 2: Cellphone Dodgem

## Citation and License
This project belongs to the Department of Computer Science, Columbia University. It may be used for educational purposes under Creative Commons **with proper attribution and citation** for the author TA **Smrithi Prakash, and the Instructor, Prof. Kenneth Ross**.

## Summary

Course: COMS 4444 Programming and Problem Solving (Fall 2023)  <br>
Problem Description: http://www.cs.columbia.edu/~kar/4444f23/node19.html<br>
Course Website: http://www.cs.columbia.edu/~kar/4444f23/4444f23.html<br>
University: Columbia University  <br>
Instructor: Prof. Kenneth Ross  <br>
Project Language: Python

### TA Designer for this project

1. Smrithi Prakash

### Teaching Assistants for Course
1. Akshay Iyer
2. Smrithi Prakash

## Installation

Requires **python3.9** or higher

Install simulator packages only

```bash
pip install -r requirements.txt
```

## Usage

### Simulator

```bash
python main.py [-ns/--no_of_stalls] [-nv/--no_to_visit] [-theta/--theta] [-T/--total_time] [-p/--players] [-s/--seed] [-g/--gui] [-sc/--scale] [-i/--interval]
```

### Running without Simulator

```bash
python main.py -g False
```

You can change the random seed, number of stalls, number of stalls to visit, theta value, timeout, list of players, and the time interval for the game loop.