import hashlib
import time
import os
import sys
import ecdsa  # Required for Elliptic Curve math

# --- Configuration & Tuning Parameters ---
MIN_RANGE = 71
MAX_RANGE = 79
DELAY_PER_KEY = 0.01  # Pauses for 10 milliseconds between keys to keep your phone cool

# Memory-mapped target database for verification
TARGET_ADDRESSES = {
    "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",
    "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",
    "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
    "1DJh2eHFYQfACPmrvpyWc8MSTYKh7w9eRF",
    "1Bxk4CQdqL9p22JEtDfdXMsng1XacifUtE",
    "15qF6X51huDjqTmF9BJgxXdt1xcj46Jmhb",
    "1ARk8HWJMn8js8tQmGUJeQHjSE7KRkn2t8"  
}

def base58_encode(b):
    """Encodes a bytes object into a Base58 string (Bitcoin standard)."""
    B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    n = int.from_bytes(b, byteorder='big')
    res = []
    while n > 0:
        n, r = divmod(n, 58)
        res.append(B58_ALPHABET[r])
    res = "".join(reversed(res))
    
    # Pad leading zero bytes with '1's
    pad = 0
    for byte in b:
        if byte == 0:
            pad += 1
        else:
            break
    return "1" * pad + res

def int_to_bitcoin_address(private_key_int):
    """Converts an integer private key into a compressed Bitcoin address (Legacy P2PKH)."""
    try:
        # 1. Convert integer to 32-byte big-endian private key
        private_key_bytes = private_key_int.to_bytes(32, byteorder='big')
        
        # 2. Generate the Public Key using SECP256k1 curve
        sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        vk = sk.verifying_key
        
        # 3. Create the Compressed Public Key (X-coordinate + parity prefix)
        x_coordinate = vk.to_string()[:32]
        y_coordinate = vk.to_string()[32:]
        if y_coordinate[-1] % 2 == 0:
            public_key_compressed = b'\x02' + x_coordinate
        else:
            public_key_compressed = b'\x03' + x_coordinate
            
        # 4. SHA-256 hash of the public key
        sha256 = hashlib.sha256(public_key_compressed).digest()
        
        # 5. RIPEMD-160 hash of the SHA-256 hash (Public Key Hash)
        ripemd160 = hashlib.new('ripemd160', sha256).digest()
        
        # 6. Add Network Byte Prefix (0x00 for Mainnet)
        network_prefix = b'\x00' + ripemd160
        
        # 7. Calculate Checksum (Double SHA-256, keep first 4 bytes)
        checksum = hashlib.sha256(hashlib.sha256(network_prefix).digest()).digest()[:4]
        
        # 8. Combine prefix, hash, and checksum, then encode to Base58
        final_binary = network_prefix + checksum
        return base58_encode(final_binary)
        
    except Exception:
        return "GenerationError"

def main():
    print("=" * 80)
    print("LAUNCHING SAFE TERMUX GENERATOR (NORMAL SPEED)")
    print(f"Target Range Boundaries : {MIN_RANGE} to {MAX_RANGE}")
    print("Pacing Governor Status  : ENABLED (Low CPU / Battery Impact)")
    print("Output File Target      : found.txt")
    print("Press Ctrl + C to exit safely at any time.")
    print("=" * 80 + "\n")
    
    current_key = MIN_RANGE
    total_scanned = 0
    start_time = time.perf_counter()
    
    try:
        while True:
            # 1. Format the key into hex format for printing
            hex_str = f"0x{current_key:064x}"
            
            # 2. Derive and check the address
            address = int_to_bitcoin_address(current_key)
            total_scanned += 1
            
            # 3. Print the execution live to the terminal screen
            sys.stdout.write(f"\r[Scanning] Key: 0x{current_key:02x} | Addr: {address[:15]}... ")
            sys.stdout.flush()
            
            # 4. Check against our target list
            if address in TARGET_ADDRESSES:
                log_entry = f"Private Key (Dec): {current_key} | Private Key (Hex): {hex_str} | Address: {address}\n"
                
                # Append the discovery immediately to found.txt
                with open("found.txt", "a") as f:
                    f.write(log_entry)
                
                print(f"\n\n[!!!] MATCH FOUND AND LOGGED: {log_entry.strip()}\n")
            
            # 5. Increment the tracking loop within bounds
            current_key += 1
            if current_key > MAX_RANGE:
                current_key = MIN_RANGE
                
            # 6. Pacing Governor: Slows the execution speed down to normal limits
            time.sleep(DELAY_PER_KEY)
            
    except KeyboardInterrupt:
        elapsed = time.perf_counter() - start_time
        avg_speed = total_scanned / elapsed if elapsed > 0 else 0
        print("\n\n" + "=" * 30 + " PIPELINE STOPPED " + "=" * 30)
        print(f"Total Keys Checked : {total_scanned:,}")
        print(f"Total Runtime      : {elapsed:.2f} seconds")
        print(f"Average Speed      : {avg_speed:.2f} keys/sec")
        print("=" * 78)

if __name__ == '__main__':
    main()
