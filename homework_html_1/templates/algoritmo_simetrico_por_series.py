# Alexander Carpio Mamani - CCOMP3-1


def gen_par(n):
    return [i for i in range(n) if i % 2 == 0 and i != 2]


def gen_impar(n, primos):
    return [i for i in range(n) if i % 2 != 0 and i not in primos]


def gen_primos(n):
    nums = []
    x = 2
    while len(nums) < n:
        primo = True
        for i in range(2, int(x**0.5) + 1):  # dom[2 , sqrt(x)]
            if x % i == 0:
                primo = False
                break
        if primo:
            nums.append(x)
        x += 1
    return nums


def get_serie(message):
    if len(message) < 2:
        return message
    if len(message) < 4:
        return message[::-1]
    n_primos = int(int(len(message) / 2 + 1) / 2 + 1)
    primos = gen_primos(n_primos)
    impares = gen_impar(len(message), primos)
    pares = gen_par(len(message))
    return primos + impares + pares


def cifrado(message):
    serie = get_serie(message)
    if type(get_serie(message)) == str:
        return serie

    codificado = ""
    for i in serie:
        codificado += message[i]
    return codificado


def descifrado(message):
    serie = get_serie(message)
    if type(get_serie(message)) == str:
        return serie

    decodificado = ""
    juntar = {serie[i]: message[i] for i in range(len(message))}
    for i in range(len(message)):
        decodificado += juntar[i]
    return decodificado


if __name__ == "__main__":
    messages = ["HOLAMUNDO", "Alexander", "FIUFIU", "", "AND", "ALGEBRA ABSTRACTA"]
    cifrados = [cifrado(m) for m in messages]
    for i in range(len(messages)):
        print(
            "original: {:s}\t encoded: {:s}\t decoded: {:s}".format(
                messages[i], cifrados[i], descifrado(cifrados[i])
            )
        )

    mensaje = "okmister"
    print(mensaje,cifrado(mensaje), descifrado(cifrado(mensaje)))
