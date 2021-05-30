import crypto

print(crypto.encryptFile('test.txt', 'password'))
print('---------------------------------------')
print(str(crypto.decryptFile('encrypted.file', 'password'), 'utf-8'))