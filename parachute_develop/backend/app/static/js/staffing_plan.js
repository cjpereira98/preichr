// Function to convert HSL to HEX
function hslToHex(h, s, l) {
    l /= 100;
    const a = s * Math.min(l, 1 - l) / 100;
    const f = n => {
        const k = (n + h / 30) % 12;
        const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        return Math.round(255 * color).toString(16).padStart(2, '0'); // Convert to hex
    };
    return `#${f(0)}${f(8)}${f(4)}`;
}

// Generate unique pastel color for each department based on index
function generatePastelColor(index) {
    const goldenAngle = 137.50776405; // Golden angle in degrees
    const hue = (index * goldenAngle) % 360; // Distribute hues using golden angle
    const saturation = 60;                   // Set saturation for pastel
    const lightness = 60;                    // Lightness for a soft pastel look
    return hslToHex(hue, saturation, lightness);
}

// Apply dynamic pastel colors to department elements
document.addEventListener("DOMContentLoaded", () => {
    const deptElements = document.querySelectorAll(".dept");
    const colorCache = {};
    let index = 0;

    deptElements.forEach(dept => {
        const department = dept.getAttribute("data-department");
        if (!colorCache[department]) {
            colorCache[department] = generatePastelColor(index);
            index++; // Increment index to generate a distinct pastel color for the next department
        }
        dept.style.borderColor = colorCache[department];
    });
});
