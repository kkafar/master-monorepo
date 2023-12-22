import numpy as np
import itertools as it


def exp() -> float:
    # Constants for ft10
    random_points: np.ndarray = np.random.random((200, 200))
    total_distance = 0
    for i in range(0, len(random_points)):
        for j in range(i + 1, len(random_points)):
            total_distance += np.linalg.norm(random_points[i] - random_points[j])

    pair_count = len(random_points) * (len(random_points) - 1) / 2
    return total_distance / pair_count

def main():
    result: np.ndarray = np.array([exp() for _ in range(100)])
    print(result.mean(), result.std())





if __name__ == "__main__":
    main()

