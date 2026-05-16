import glassescat_agent

n = glassescat_agent.GlassescatAgent()

print("\n=== Test: Bilinmeyen uygulama ===")
result = n.process("ac snapchat")
print(f"ac snapchat: {result}")

print("\n=== Test: Uygulama ara snapchat ===")
result = n.process("uygulama ara snapchat")
print(result)

print("\n=== Test: snapchat ara ===")
result = n.process("snapchat ara")
print(result)

print("\n=== Test: bul discord ===")
result = n.process("bul discord")
print(result)