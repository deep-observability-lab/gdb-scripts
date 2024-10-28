import paramiko

client = paramiko.SSHClient()



client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.183.132',22,'zahra','1233zahra')
client.get_transport()

command = "sudo su -c 'cat /etc/shadow'"
stdin, stdout, stderr = client.exec_command(command=command,get_pty=True)
print("Original command sent!")
stdin.write("1233zahra\n")
print("Password sent!")
stdin.flush()
print("Input flushed!")
print( "output  " , stdout.read().decode() ) 
if stderr.channel.recv_exit_status() != 0:
    print("Error occured!")
    print(f"The following error occured: {stderr.readlines()}")
else:
    print("Getting output!")
    print(f"The following output was produced: \n{stdout.readlines()}")

client.close()
