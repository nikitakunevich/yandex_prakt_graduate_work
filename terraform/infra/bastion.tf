data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "bastion" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t3.micro"
  associate_public_ip_address = true
  subnet_id                   = aws_subnet.eks[0].id
  vpc_security_group_ids      = [aws_security_group.bastion.id]
  key_name                    = aws_key_pair.bastion.id
  user_data                   = file("scripts/deploy-elasticsearch.sh")

  tags = {
    Name = "Bastion"
  }
}

resource "aws_key_pair" "bastion" {
  key_name   = "bastion-key"
  public_key = file("files/bastion-ssh-keys/bastion_ssh_key.pub")
}

output "bastion-ip" {
  value = aws_instance.bastion.public_ip
}
