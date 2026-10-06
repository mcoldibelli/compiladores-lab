// Programa do grupo: raiz quadrada pelo metodo de Newton.
//
// A cada passo, o palpite x vira (x + n / x) / 2, que fica mais perto da
// raiz de n. O calculo para quando um passo muda o palpite em menos de
// 0.0000001.

funcao real distancia(real a, real b) {
  se (a > b) {
    retorne a - b;
  }
  retorne b - a;
}

// Recursiva: cada chamada e um passo do metodo.
funcao real raiz(real n, real x) {
  real proximo = (x + n / x) / 2.0;
  se (distancia(proximo, x) < 0.0000001) {
    retorne proximo;
  }
  retorne raiz(n, proximo);
}

funcao vazio mostrar(real n) {
  escreva("raiz quadrada de");
  escreva(n);
  real r = raiz(n, n / 2.0 + 1.0);
  escreva(r);
  escreva("conferindo, r * r:");
  escreva(r * r);
}

funcao vazio principal() {
  mostrar(2);
  mostrar(144);
  mostrar(0.25);
  mostrar(1000);
}
