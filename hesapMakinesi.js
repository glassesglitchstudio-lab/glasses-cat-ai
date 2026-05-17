// Basit bir hesap makinesi JavaScript kodu

function hesapla(islem, sayi1, sayi2) {
    switch (islem) {
        case 'toplama':
            return sayi1 + sayi2;
        case 'cikarma':
            return sayi1 - sayi2;
        case 'carpma':
            return sayi1 * sayi2;
        case 'bolme':
            if (sayi2 !== 0) {
                return sayi1 / sayi2;
            } else {
                return 'Bolme islemi 0'a bolunemez.';
            }
        default:
            return 'Gecersiz islem.';
    }
}

// Kullanım ornegi
console.log(hesapla('toplama', 10, 5)); // 15
console.log(hesapla('cikarma', 10, 5)); // 5
console.log(hesapla('carpma', 10, 5)); // 50
console.log(hesapla('bolme', 10, 5)); // 2
console.log(hesapla('bolme', 10, 0)); // Bolme islemi 0'a bolunemez.
console.log(hesapla('uslus', 10, 5)); // Gecersiz islem.