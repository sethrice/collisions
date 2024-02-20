#!/usr/bin/env python3

# A detectcoll log parser with collision signatures
# based on message and intermediate hash values differentials

# usage detectcoll <file> | logparse.py

# Ange Albertini 2024
# With the help of Marc Stevens

import sys

# Warning: there could be... collisions (!) in dIhv sigs.
sigs = {  # dMsg, dIhv
    "APop": ["", "31,31,31,31"],
    "Wang": ["4,11,14", "31,31,25,31,26,25,31,25"],
    "FastColl": ["4,11,14", "31,31,25,31,25,31,25"],
    "Unicoll1": ["2", None],
    "Unicoll3": ["6,9,15", None],
    "HashClashCPC": ["11", None],
    "SingleCPC": ["2,4,11,14", "10,9,8,7,6,5,30,29,28,26,24,22,20,17,14,11,5,26,25,23,22,5,25,9,8,7,6,5"],
    "SingleIPC": ["8,13", ""],
    "SHAttered0": ["0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15", ""],
    "SHAttered1": ["0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15", "12,11,10,9,5,4,2,1,8,7,5,4,1,31"],
    "Shambles": ["0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15", "12,9,7,6,5,4,1,8,7,5,4,1,1,31"],
}


def make_dihv_sig(ihv1: str, ihv2: str) -> str:
    indexes = []
    for index in range(0, len(ihv1), 8):
        word1 = format(int(ihv1[index: index+8], 16), '032b')
        word2 = format(int(ihv2[index: index+8], 16), '032b')
        for index, char in enumerate(word1):
            if char != word2[index]:
                indexes += [str(31-index)]

    result = ",".join(indexes)
    return result


def make_dm_sig(dms: list) -> str:
    return ",".join([dm.split("=")[0][2:] for dm in dms])


def match_sig(blockNb: int, sig_dms: str, dihv_sig: str) -> None:
    for sig in sigs:
        if (sigs[sig][0] == sig_dms):
            if (sigs[sig][1] is None) or ((sigs[sig][1] is not None) and sigs[sig][1] == dihv_sig):
                print(f"block: {blockNb}, collision: {sig}")
                return
    else:
        print("Nothing found:", repr(dihv_sig), repr(sig_dms))
    return


def main():
    step = 0
    ihv1 = None
    ihv2 = None
    dms = None
    blockNb = None

    for line in sys.stdin:
        line = line.strip()
        if (step == 0) and (line.startswith('Found collision in block ')):
            block_s = line.split(" ")[4]
            if block_s.endswith(":"):  # Sha1 blocks have more information
                block_s = block_s[:-1]
            blockNb = int(block_s)
            step = 1

        elif (step == 1) and (line.startswith('dm:')):
            dms = line.split(" ")[1:]
            dm_sig = make_dm_sig(dms)
            step = 2

        elif (step == 2) and (line.startswith('ihv1')):
            _, ihv1 = line.split("=")
            assert len(ihv1) % 8 == 0
            step = 3

        elif (step == 3) and (line.startswith('ihv2')):
            _, ihv2 = line.split("=")
            assert len(ihv2) == len(ihv1)
            dihv_sig = make_dihv_sig(ihv1, ihv2)

            match_sig(blockNb, dm_sig, dihv_sig)
            step = 0


if __name__ == '__main__':
    main()