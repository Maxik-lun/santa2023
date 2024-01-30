from process_utils import parse_gap_data
import pandas as pd


if __name__ == '__main__':
    # Load Data
    # INPUT_DIR = '/kaggle/input/santa-2023'
    puzzle_info_path = './puzzle_info.csv'
    puzzle_path = './puzzles.csv'
    ss_path = './sample_submission.csv'
    puzzles_df = pd.read_csv(puzzle_path)
    puzzle_info_df = pd.read_csv(puzzle_info_path)
    ss_df = pd.read_csv(ss_path)
    gap_dir = "./gap_data/"
    # gap_dict = {}
    ptypes = puzzles_df['puzzle_type'].unique()
    for ptype in ptypes[13:]:
        gensi = eval(puzzle_info_df[puzzle_info_df.puzzle_type == ptype].allowed_moves.values[0])
        N = max([max(gensi[g]) for g in gensi])+1
        base, sgs = parse_gap_data(gap_dir, ptype, N, debug=False)
        print(ptype, len(base), len(sgs))