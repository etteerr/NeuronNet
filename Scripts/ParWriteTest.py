import Engine.ParWrite as pw
if __name__ == '__main__':
    file = pw.ParWriter('test.txt', mode='w')
    file.write('Hello!')
    file.write('How ist going?')
    file.write('Line\nNew line')
    file.close()

