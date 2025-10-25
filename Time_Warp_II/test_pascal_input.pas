program InputTest;
var
  name: string;
  age: integer;
begin
  writeln('Welcome to Pascal input test!');
  write('Please enter your name: ');
  readln(name);
  write('Please enter your age: ');
  readln(age);
  writeln('Hello, ', name, '! You are ', age, ' years old.');
end.