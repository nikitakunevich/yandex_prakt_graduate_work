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

  connection {
    type        = "ssh"
    host        = aws_instance.bastion.public_ip
    user        = "ubuntu"
    private_key = file("files/bastion-ssh-keys/bastion_ssh_key")
  }

  provisioner "file" {
    source      = "files/es-schema/es.genres.schema.json"
    destination = "/home/ubuntu/es.genres.schema.json"
  }

  provisioner "file" {
    source      = "files/es-schema/es.movies.schema.json"
    destination = "/home/ubuntu/es.movies.schema.json"
  }

  provisioner "file" {
    source      = "files/es-schema/es.persons.schema.json"
    destination = "/home/ubuntu/es.persons.schema.json"
  }

  provisioner "remote-exec" {
    inline = [
      "sleep 600",
      "curl  -XPUT http://localhost:9200/movies -H 'Content-Type: application/json' -d @/home/ubuntu/es.movies.schema.json",
      "curl  -XPUT http://localhost:9200/persons -H 'Content-Type: application/json' -d @/home/ubuntu/es.persons.schema.json",
      "curl  -XPUT http://localhost:9200/genres -H 'Content-Type: application/json' -d @/home/ubuntu/es.genres.schema.json"
    ]
  }
}

resource "aws_key_pair" "bastion" {
  key_name   = "bastion-key"
  public_key = file("files/bastion-ssh-keys/bastion_ssh_key.pub")
}

output "bastion-ip" {
  value = aws_instance.bastion.public_ip
}

output "bastion-private-ip" {
  value = aws_instance.bastion.private_ip
}
