const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const PDFParser = require("pdf2json");
const cors = require('cors');

const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, uploadDir),
    filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname)
});
const upload = multer({ storage });

app.post('/upload', upload.single('resume'), (req, res) => {
    if (!req.file) return res.status(400).json({ error: "No file uploaded." });

    const pdfParser = new PDFParser(null, 1);

    pdfParser.on("pdfParser_dataError", errData => res.status(500).json({ error: "Parsing Failed" }));

    pdfParser.on("pdfParser_dataReady", pdfData => {
        const extractedText = pdfParser.getRawTextContent();
        const textLower = extractedText.toLowerCase();

        const skillLibrary = [
            "react", "node.js", "express", "python", "java", "javascript",
            "mongodb", "mysql", "html", "css", "git", "github", "c++", "cpp", "c ",
            "numpy", "pandas", "tailwind", "aws", "machine learning", "opencv",
            "data structures", "algorithms", "rest apis", "blockchain"
        ];

        let matchedSkills = [];
        skillLibrary.forEach(skill => {
 
            if (textLower.includes(skill)) {
                let displaySkill = skill.toUpperCase();
                if (skill === "cpp" || skill === "c++" || skill === "c ") displaySkill = "C/C++";
                if (!matchedSkills.includes(displaySkill)) matchedSkills.push(displaySkill);
            }
        });

        const allDecimals = extractedText.match(/\b([6-9]\.\d{1,2}|10\.0)\b/g);
        let foundCGPA = allDecimals ? Math.max(...allDecimals.map(Number)) : "Not Detected";

        let status = "Fresher / Student";
        if (textLower.includes("present") || textLower.includes("intern")) {
            status = "Early Career / Final Year";
        }

        let skillWeight = (matchedSkills.length / 15) * 70; 
        if (skillWeight > 70) skillWeight = 70;

        let educationWeight = (foundCGPA !== "Not Detected") ? 30 : 0;
        let finalScore = Math.round(skillWeight + educationWeight);

        const finalJSON = {
            status: "success",
            atsScore: finalScore + "%",
            details: {
                name: "Ishita Chaturvedi",
                matchedSkills: matchedSkills,
                cgpaFound: foundCGPA,
                experienceStatus: status,
                isShortlisted: finalScore >= 55
            }
        };

        const jsonPath = path.join(uploadDir, `${req.file.filename}.json`);
        fs.writeFileSync(jsonPath, JSON.stringify(finalJSON, null, 2));

        console.log(`\n✅ Result for ${req.file.originalname}: ${finalScore}%`);
        res.json(finalJSON);
    });

    pdfParser.loadPDF(req.file.path);
});

app.listen(port, () => console.log(`Smart ATS Server: http://localhost:${port}`));
