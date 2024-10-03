import ipaddress

cidrs = [
    "2001:4860:4801:10::/64", "2001:4860:4801:11::/64", # ... add the rest here
    "66.249.79.96/27"
]

for cidr in cidrs:
    net = ipaddress.ip_network(cidr, strict=False)
    print(f"Network: {net.network_address}")
    print(f"Broadcast: {net.broadcast_address}")
    print(f"Usable IP range: {list(net.hosts())[0]} to {list(net.hosts())[-1]}")
    print(f"Total Usable IPs: {net.num_addresses - 2}")  # Subtracting network and broadcast for IPv4
    print()