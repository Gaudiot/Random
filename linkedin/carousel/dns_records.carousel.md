---

# 🎠 Carrossel

---

# Slide 1 — What are they?

## Title

### **What Are DNS Records?**

## Body

DNS Records are instructions stored inside a DNS Server.

They tell the internet things like:

* where a domain points to
* how subdomains work
* where emails should go

You can think of them as rules for handling DNS requests.

They also support a TTL value:
→ how long the information stays cached before checking again.

---

# Slide 2 — A / AAAA Record

## Title

### **A / AAAA Records**

## Body

These records connect a domain name to an IP address.

Example:

victorgaudiot.com
↓
135.62.193.56

* A Record → IPv4
* AAAA Record → IPv6

They are the foundation of how websites become reachable on the internet.

---

# Slide 3 — CNAME

## Title

### **CNAME Record**

## Body

A CNAME works like a DNS alias.

Example:

[www.example.com](http://www.example.com)
↓
app.example.com

Very common for:

* subdomains
* external services
* platforms like Vercel

Instead of using:
myapp.vercel.app

You can use:
awesomeapp.com

---

# Slide 4 — MX

## Title

### **MX Record**

## Body

MX stands for Mail Exchanger.

These records define which servers receive emails for your domain.

Example:
yourdomain.com
↓
Google Workspace / Gmail

MX records also support priorities:

* smaller number = higher priority

This helps create email redundancy and failover systems.

---

# Slide 5 — NS

## Title

### **NS Record**

## Body

NS stands for Name Server.

These records tell the internet:
“Which DNS server knows more about this domain?”

They are responsible for delegating DNS authority.

Example:

* home.website.com
* api.website.com
* shop.website.com

The NS record points to the server that knows how to resolve them.

---

# Slide 6 — TXT

## Title

### **TXT Record**

## Body

TXT Records store arbitrary text data.

They are commonly used for:

* domain verification
* email security
* third-party integrations

Example:

keybase-site-verification=random_token

This allows services to confirm you really own the domain.

TXT records are also heavily used for:

* SPF
* DKIM
* DMARC

(email authentication systems)