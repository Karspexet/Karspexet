export function randomChoice<T>(choice: T[]): T {
  var index = Math.floor(Math.random() * choice.length);
  return choice[index];
}

export function timeout(func: Function) {
  let timer: number = 0;
  return {
    queue: (t: number) => {
      timer = setTimeout(func, t);
    },
    cancel: () => {
      clearTimeout(timer);
    },
  };
}

export function sum(arr: number[]): number {
  let result = 0;
  for (let value of arr) {
    result += value;
  }
  return result;
}
