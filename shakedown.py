# This will be some kind of stochastic search for a canon melody.

import numpy as np
from time import perf_counter

rng = np.random.default_rng()

##  INFRASTRUCTURE  ###########################################################

def isDiatonic(pitchSet):
  # the pitch set is assumed to be a numpy array of pitches
  spc = np.sort(np.mod(5*pitchSet.flatten(), 12))
  maxGap = max(np.max(np.diff(spc)), spc[0]+12-spc[-1])
  return maxGap >= 6

def melToDyads(melody):
  return np.vstack((melody, np.roll(melody, L - delay) + xp))

def penalty(dyads):
  return (
    sum(np.mod(dyads[1,l]-dyads[0,l],12) not in conson for l in range(L))
    + sum(np.mod(dyads[0,:]-np.roll(dyads[1,:],1),12)==0) # pitch relay
    + sum(np.mod(dyads[0,:]-np.roll(dyads[1,:],-1),12)==0) # & the other way
    + sum(1 for l in range(L) if not
    isDiatonic(np.roll(dyads,l,axis=1)[:,:2])))

def findOneSolution(delay,xp):
  print(f'Searching with {delay=} and {xp=}.')
  startSearch = perf_counter()
  melody = rng.choice(scale, size=L)
  while len(set(melody)) < minDistPCs:
    melody = rng.choice(scale, size=L)
  pen = penalty(melToDyads(melody))
  while pen > 0:
    now = perf_counter()
    if perf_counter() > startSearch + 10:
      print(f'  Timed out with penalty {pen}.')
      break
    bestpen = np.inf
    for l in range(L):
      for p in scale:
        if p != melody[l]:
          candmel = melody.copy()
          candmel[l] = p
          if len(set(candmel)) >= minDistPCs:
            candpen = penalty(melToDyads(candmel))
            if candpen < bestpen:
              pool = []
              bestpen = candpen
            if candpen == bestpen:
              pool.append(candmel)
    if bestpen > pen:
      print(f'  Panicked at local minimum, with penalty {pen}:')
      print(melToDyads(melody))
      break
    melody = rng.choice(pool)
    pen = bestpen
  return (pen,melody)

def printHarmonicSegmentation(dyads):
  """
  Find a minimum-segment harmonic analysis of dyads, then print:

  chord symbols
  first voice
  second voice

  Each dyad occupies a 7-character column.
  """

  L = dyads.shape[1]

  chord_types = [
    ('',      {0, 4, 7}),        # major
    ('m',     {0, 3, 7}),        # minor
    ('7',     {0, 4, 7, 10}),    # dominant 7
    ('maj7',  {0, 4, 7, 11}),    # major 7
    ('m7',    {0, 3, 7, 10}),    # minor 7
    ('m7b5',  {0, 3, 6, 10}),    # half diminished
    ('dim7',  {0, 3, 6, 9}),     # diminished 7
  ]

  # For each possible segment [i:j], find the first chord in our
  # preference order which contains all its pitch classes.
  segment_chord = {}

  for i in range(L):
    pcs = set()

    for j in range(i + 1, L + 1):
      pcs.update(np.mod(dyads[:, j - 1], 12))

      for suffix, chord in chord_types:
        for root in range(12):
          chord_pcs = {(root + x) % 12 for x in chord}

          if pcs.issubset(chord_pcs):
            segment_chord[i, j] = notes[root] + suffix
            break
        else:
          continue

        break

  def segmentCost(length):
    return {1:6,2:3,3:1}.get(length,0)

  # dp[j] = minimum cost of segments covering dyads [:j].
  # prev[j] records the final segment of the best solution ending at j.
  INF = 6*L + 1
  dp = np.full(L + 1, INF, dtype=int)
  prev = [None] * (L + 1)
  dp[0] = 0

  for j in range(1, L + 1):
    for i in range(j):
      if dp[i] == INF:
        continue

      chord_name = segment_chord.get((i, j))

      if chord_name is not None and dp[i] + segmentCost(j-i) < dp[j]:
        dp[j] = dp[i] + segmentCost(j-i)
        prev[j] = (i, chord_name)

  if dp[L] == INF:
    print("No valid harmonic segmentation")
    print(dp)
  else:
    # Recover the segments backwards.
    segments = []

    j = L
    while j > 0:
      (i, chord_name) = prev[j]
      segments.append((i, j, chord_name))
      j = i

    segments.reverse()

    # Construct the chord-symbol line. Each dyad has a 4-character column.
    chord_line = ['       '] * L

    for start, end, chord_name in segments:
      chord_line[start] = chord_name.ljust(7)

    print(''.join(chord_line))

  # Print the two voices in corresponding 4-character columns.
  for voice in dyads:
    print(''.join(f'{pitch:>2}     ' for pitch in voice))

##  INITIALISATION  ###########################################################

L = 16  #  melody length
delays = np.array([5,7,9,11])
xposes = np.array([3,4])  #  I think 8 & 9 are redundant; (5,3)~(11,8)?
scale = np.array([0,2,4,7,9,11])
conson = {3,4,5,7,8,9}
notes = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
minDistPCs = 3

##  MAIN LOOP  ################################################################

attempts = {(delay,xp):0 for delay in delays for xp in xposes}
successes = {(delay,xp):0 for delay in delays for xp in xposes}
for it in range(100):
  delay = rng.choice(delays)
  xp = rng.choice(xposes)
  (pen,melody) = findOneSolution(delay, xp)
  attempts[(delay,xp)] += 1
  if pen == 0:
    successes[(delay,xp)] += 1
    dyads = melToDyads(melody)
    printHarmonicSegmentation(dyads)

print('(delay,xp,successes/attempts):')
for delay in delays:
  for xp in xposes:
    print(f'({delay:2},{xp},{successes[delay,xp]:2}/{attempts[delay,xp]:2})   ', end='')
  print()
