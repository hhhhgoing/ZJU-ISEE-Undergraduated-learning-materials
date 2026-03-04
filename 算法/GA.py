import numpy as np
import os
import time
import cv2
import random

target_img_path = "assets/mona_lisa.png"
shape = (256, 256)
pop_size = 18
generations = 10000
crossover_rate = 0.5
mutation_rate = 0.001


def load_target_image(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img = cv2.resize(img, shape)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def create_individual():
    return "".join(
        random.choices(["0", "1"], k=7200)
    )  # 100 个三角形，每个三角形 10 个参数（r,g,b,a 和 三组坐标），每个参数 8 位


def decode_individual(individual, alpha=0.5):
    individual = np.dot(
        np.array(list(individual), dtype=np.uint8).reshape(-1, 8),
        2 ** np.arange(7, -1, -1),
    ).tolist()  # 二进制转换为十进制

    img = np.ones((256, 256, 3), dtype=np.uint8) * 255  # 白色背景
    for i in range(0, len(individual), 9):
        overlay = img.copy()
        color = (individual[i], individual[i + 1], individual[i + 2])
        p1 = (individual[i + 3], individual[i + 4])
        p2 = (individual[i + 5], individual[i + 6])
        p3 = (individual[i + 7], individual[i + 8])
        cv2.fillPoly(overlay, [np.array([p1, p2, p3])], color)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    return img


def fitness(individual):
    generated_img = decode_individual(individual)
    return 1 - np.sum(np.abs(generated_img.astype(int) - target_img.astype(int))) / (
        shape[0] * shape[1] * 3 * 255
    )


def select(population, fitnesses, num):
    total_fitness = sum(fitnesses)
    probabilities = np.array(fitnesses) / total_fitness
    selected = random.choices(population, probabilities, k=num)
    return selected


def crossover(population):
    for i in range(0, len(population), 2):
        if random.random() < crossover_rate:
            crossover_mask = random.choices([0, 1], k=7200)
            a_arr = np.array(list(population[i]))
            b_arr = np.array(list(population[i + 1]))
            a_new_arr = np.where(crossover_mask, a_arr, b_arr)
            b_new_arr = np.where(crossover_mask, b_arr, a_arr)
            population[i] = "".join(a_new_arr)
            population[i + 1] = "".join(b_new_arr)


def mutate(population):
    population = np.array([list(individual) for individual in population], dtype=int)
    mutation_mask = np.random.rand(len(population), 7200) < mutation_rate
    population = population ^ mutation_mask
    population = ["".join(map(str, individual)) for individual in population]
    return population


def main():
    population = [create_individual() for _ in range(pop_size)]

    for gen in range(generations):
        fitnesses = [fitness(individual) for individual in population]
        top_2_index = np.argsort(fitnesses)[-2:]
        top_2 = [population[i] for i in top_2_index]

        # 选择
        new_population = select(population, fitnesses, pop_size - 2)

        # 交叉
        crossover(new_population)

        # 变异
        new_population = mutate(new_population)

        population = top_2 + new_population

        if (gen + 1) % 100 == 0 or (gen + 1) == 1:
            best = top_2[-1]
            print(
                f"Generation {gen + 1}, fitness: {fitnesses[top_2_index[-1]]}, diversity: {len(set(population))}"
            )
            cv2.imwrite(
                f"gen_{gen + 1}.png",
                cv2.cvtColor(decode_individual(best), cv2.COLOR_RGB2BGR),
            )

    cv2.imwrite(
        "final.png", cv2.cvtColor(decode_individual(top_2[-1]), cv2.COLOR_RGB2BGR)
    )


if __name__ == "__main__":
    target_img_path = (
        input("请输入目标图片路径(留空默认为 assets/mona_lisa.png)：")
        or target_img_path
    )
    global target_img
    target_img = load_target_image(target_img_path)
    folder_name = time.strftime("%m-%d %H:%M", time.localtime())
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        os.chdir(folder_name)
    else:
        print(f"文件夹 {folder_name} 已存在，请删除后重试")
        exit(1)
    main()
