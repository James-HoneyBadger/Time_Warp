program HelloPascal;
var
  x, y: integer;
  name: string;
  pi_val: real;
  flag: boolean;

begin
  x := 42;
  y := x * 2;
  name := 'Turbo Pascal';
  pi_val := 3.14159;
  flag := true;

  writeln('Hello from ', name);
  writeln('x = ', x);
  writeln('y = ', y);
  writeln('pi = ', pi_val);

  if flag then
    writeln('Flag is true')
  else
    writeln('Flag is false');
end.