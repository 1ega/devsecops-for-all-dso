resource "aws_security_group" "admin" {
  description = "Test-only group"
  ingress {
    description = "Test-only ingress"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["10.10.0.0/24"]
  }
}
