// Script contoh untuk testing obfuscator
// Ini akan menampilkan beberapa output untuk membuktikan kode berjalan

function greeting() {
    console.log("=".repeat(50));
    console.log("  SCRIPT INI BERHASIL DIJALANKAN!");
    console.log("=".repeat(50));
    console.log();
}

function showInfo() {
    console.log(`Waktu: ${new Date().toISOString()}`);
    console.log(`Node.js: ${process.version}`);
    console.log(`Platform: ${process.platform}`);
    console.log(`Working dir: ${process.cwd()}`);
    console.log();
}

function calculate() {
    console.log("Test perhitungan:");
    for (let i = 1; i <= 5; i++) {
        const result = i ** 2;
        console.log(`  ${i}^2 = ${result}`);
    }
    console.log();
}

function secretMessage() {
    const message = "Ini adalah pesan rahasia yang ter-obfuscate!";
    console.log(`Pesan: ${message}`);
    console.log();
}

function main() {
    greeting();
    showInfo();
    calculate();
    secretMessage();
    console.log("Script selesai dengan sukses!");
}

main();
