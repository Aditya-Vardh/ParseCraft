(function applySavedTheme() {
    if (localStorage.getItem("ParseCraft-theme") === "dark") {
        document.body.classList.add("dark-mode");
    }
})();

document.addEventListener("DOMContentLoaded", () => {
    const grammarInput = document.querySelector("textarea[name='grammar']");
    const testInput = document.querySelector("input[name='test_string']");
    const sampleButtons = document.querySelectorAll("[data-sample]");
    const results = document.querySelector("#results");
    const themeToggle = document.querySelector("#theme-toggle");
    const downloadReport = document.querySelector("#download-report");
    const cards = document.querySelectorAll(".card");
    const pipelineStages = document.querySelectorAll(".pipeline-stage");
    const consoleLines = document.querySelectorAll(".console-line");
    const explainButtons = document.querySelectorAll("[data-explain]");

    const samples = {
        arithmetic: {
            grammar: [
                "E->TE'",
                "E'->+TE'|epsilon",
                "T->FT'",
                "T'->*FT'|epsilon",
                "F->(E)|id",
            ].join("\n"),
            input: "id+id*id",
        },
        simple: {
            grammar: [
                "S->AB",
                "A->a|epsilon",
                "B->b",
            ].join("\n"),
            input: "ab",
        },
        boolean: {
            grammar: [
                "B->T B'",
                "B'->or T B'|epsilon",
                "T->F T'",
                "T'->and F T'|epsilon",
                "F->not F|( B )|id",
            ].join("\n"),
            input: "id and id",
        },
        assignment: {
            grammar: [
                "S->id=E",
                "E->TE'",
                "E'->+TE'|epsilon",
                "T->FT'",
                "T'->*FT'|epsilon",
                "F->id",
            ].join("\n"),
            input: "id=id+id",
        },
    };

    function loadSample(name) {
        const sample = samples[name];
        if (!sample || !grammarInput || !testInput) {
            return;
        }

        grammarInput.value = sample.grammar;
        testInput.value = sample.input;
        grammarInput.focus();
    }

    function updateThemeButton() {
        if (!themeToggle) {
            return;
        }

        const isDark = document.body.classList.contains("dark-mode");
        const label = themeToggle.querySelector(".theme-label");

        if (label) {
            label.textContent = isDark ? "Light Mode" : "Dark Mode";
        }
    }

    function stringifyValue(value) {
        if (Array.isArray(value)) {
            return value.join(", ");
        }

        if (value && typeof value === "object") {
            return JSON.stringify(value);
        }

        return value ?? "";
    }

    function readReportData() {
        const dataNode = document.querySelector("#report-data");
        if (!dataNode) {
            return null;
        }

        return JSON.parse(dataNode.textContent);
    }

    function animatePipeline() {
        pipelineStages.forEach((stage, index) => {
            setTimeout(() => {
                pipelineStages.forEach((item, innerIndex) => {
                    item.classList.toggle("is-complete", innerIndex < index);
                    item.classList.toggle("is-active", innerIndex === index);
                });

                if (index === pipelineStages.length - 1) {
                    setTimeout(() => {
                        pipelineStages.forEach((item) => {
                            item.classList.add("is-complete");
                            item.classList.remove("is-active");
                        });
                    }, 520);
                }
            }, index * 520);
        });
    }

    function typeConsoleLine(line, text, done) {
        let index = 0;
        line.classList.add("is-visible", "is-typing");

        const timer = setInterval(() => {
            line.textContent = text.slice(0, index + 1);
            index += 1;

            if (index >= text.length) {
                clearInterval(timer);
                line.classList.remove("is-typing");
                done();
            }
        }, 14);
    }

    function animateConsole() {
        const lines = Array.from(consoleLines);

        function next(index) {
            if (index >= lines.length) {
                return;
            }

            const line = lines[index];
            typeConsoleLine(line, line.dataset.log || "", () => {
                setTimeout(() => next(index + 1), 130);
            });
        }

        next(0);
    }

    function explainText(kind, data) {
        if (!data) {
            return "";
        }

        if (kind === "first") {
            const nullable = Array.isArray(data.nullableSymbols) && data.nullableSymbols.length
                ? data.nullableSymbols.join(", ")
                : "none";
            return `FIRST was computed from the transformed grammar by collecting terminals that can start each non-terminal. Nullable symbols: ${nullable}.`;
        }

        if (kind === "follow") {
            const symbols = data.follow ? Object.keys(data.follow).join(", ") : "the grammar symbols";
            return `FOLLOW was computed by scanning production positions and propagating lookahead terminals. The tracked non-terminals are ${symbols}.`;
        }

        const conflicts = Array.isArray(data.conflicts) ? data.conflicts.length : 0;
        return conflicts === 0
            ? "The LL(1) table has one production per filled cell, so the parser can choose rules from one lookahead token."
            : `The LL(1) table reports ${conflicts} conflict(s). Conflicting cells mean more than one production competes for the same lookahead.`;
    }

    function setExplanationPanels() {
        const data = readReportData();

        explainButtons.forEach((button) => {
            const target = document.querySelector(`#explain-${button.dataset.explain}`);
            if (target && data) {
                target.textContent = explainText(button.dataset.explain, data);
            }

            button.addEventListener("click", () => {
                if (target) {
                    target.classList.toggle("is-open");
                    button.textContent = target.classList.contains("is-open") ? "Hide" : button.dataset.explain === "ll1" ? "Explain LL(1)" : "Explain";
                }
            });
        });
    }

    function pdfSafe(text) {
        return String(text ?? "")
            .replace(/[^\x09\x0A\x0D\x20-\x7E]/g, "?")
            .replace(/\\/g, "\\\\")
            .replace(/\(/g, "\\(")
            .replace(/\)/g, "\\)");
    }

    function wrapText(text, maxChars) {
        const words = String(text ?? "").split(/\s+/);
        const lines = [];
        let current = "";

        words.forEach((word) => {
            if (!word) {
                return;
            }

            if ((current + " " + word).trim().length > maxChars && current) {
                lines.push(current);
                current = word;
            } else {
                current = `${current} ${word}`.trim();
            }
        });

        if (current) {
            lines.push(current);
        }

        return lines.length ? lines : [""];
    }

    function createPdfReport(data) {
        const pageWidth = 595;
        const pageHeight = 842;
        const margin = 48;
        const bottom = 62;
        const pages = [];
        let commands = [];
        let y = pageHeight - margin;

        function color(hex) {
            const value = hex.replace("#", "");
            const r = parseInt(value.slice(0, 2), 16) / 255;
            const g = parseInt(value.slice(2, 4), 16) / 255;
            const b = parseInt(value.slice(4, 6), 16) / 255;
            return `${r.toFixed(3)} ${g.toFixed(3)} ${b.toFixed(3)}`;
        }

        function addCommand(command) {
            commands.push(command);
        }

        function text(x, textY, value, size = 10, font = "F1", fill = "#111827") {
            addCommand(`BT /${font} ${size} Tf ${color(fill)} rg ${x} ${textY} Td (${pdfSafe(value)}) Tj ET`);
        }

        function rect(x, rectY, width, height, fill, stroke) {
            if (fill) {
                addCommand(`${color(fill)} rg ${x} ${rectY} ${width} ${height} re f`);
            }
            if (stroke) {
                addCommand(`${color(stroke)} RG ${x} ${rectY} ${width} ${height} re S`);
            }
        }

        function newPage() {
            if (commands.length) {
                pages.push(commands);
            }
            commands = [];
            y = pageHeight - margin;
        }

        function ensure(height) {
            if (y - height < bottom) {
                newPage();
            }
        }

        function heading(title) {
            ensure(44);
            text(margin, y, title, 16, "F2", "#1d4ed8");
            y -= 24;
            rect(margin, y + 8, pageWidth - margin * 2, 1, "#bfdbfe");
            y -= 14;
        }

        function paragraph(value) {
            wrapText(value, 88).forEach((line) => {
                ensure(16);
                text(margin, y, line, 10, "F1", "#334155");
                y -= 14;
            });
            y -= 6;
        }

        function linesBlock(lines) {
            const values = Array.isArray(lines) ? lines : [lines];
            values.forEach((line) => {
                ensure(15);
                text(margin + 8, y, line || " ", 9, "F3", "#0f172a");
                y -= 13;
            });
            y -= 8;
        }

        function keyValueTable(rows) {
            const rowHeight = 22;
            rows.forEach(([key, value], index) => {
                ensure(rowHeight + 2);
                rect(margin, y - rowHeight + 7, pageWidth - margin * 2, rowHeight, index % 2 ? "#f8fafc" : "#eef2ff", "#dbe3ef");
                text(margin + 10, y - 7, key, 9, "F2", "#1e293b");
                text(margin + 190, y - 7, stringifyValue(value), 9, "F1", "#1e293b");
                y -= rowHeight;
            });
            y -= 10;
        }

        function mapTable(map) {
            const rows = Object.entries(map || {}).map(([key, value]) => [key, stringifyValue(value)]);
            keyValueTable(rows.length ? rows : [["No data", ""]]);
        }

        function parsingTable() {
            const columns = data.tableColumns || [];
            const header = ["Non-terminal", ...columns].join(" | ");
            linesBlock([header, "-".repeat(Math.min(header.length, 110))]);
            (data.tableRows || []).forEach((row) => {
                const values = columns.map((column) => stringifyValue(row[column]) || "-");
                wrapText([row.non_terminal, ...values].join(" | "), 104).forEach((line) => {
                    ensure(14);
                    text(margin + 8, y, line, 8, "F3", "#0f172a");
                    y -= 12;
                });
                y -= 3;
            });
            y -= 8;
        }

        function simulationTable() {
            (data.simulation || []).forEach((step, index) => {
                const line = `${index + 1}. Stack: ${step.stack} | Input: ${step.input} | Action: ${step.action}`;
                wrapText(line, 104).forEach((part) => {
                    ensure(14);
                    text(margin + 8, y, part, 8, "F3", "#0f172a");
                    y -= 12;
                });
                y -= 3;
            });
            y -= 8;
        }

        rect(0, 0, pageWidth, pageHeight, "#eff6ff");
        rect(0, pageHeight - 180, pageWidth, 180, "#1d4ed8");
        text(margin, pageHeight - 92, "ParseCraft", 34, "F2", "#ffffff");
        text(margin, pageHeight - 124, "Professional Compiler IDE Report", 16, "F1", "#dbeafe");
        text(margin, pageHeight - 170, `Timestamp: ${new Date().toLocaleString()}`, 10, "F1", "#ffffff");
        y = pageHeight - 232;
        heading("Project");
        keyValueTable([
            ["Project", data.project || "ParseCraft"],
            ["Test String", data.testString || ""],
            ["Final Result", data.accepted ? "Accepted" : "Rejected"],
        ]);

        heading("Grammar Statistics");
        keyValueTable([
            ["Grammar Type", data.stats?.grammar_type || ""],
            ["LL(1) Status", data.stats?.is_ll1 ? "LL(1)" : "Not LL(1)"],
            ["Non Terminals", data.stats?.non_terminals ?? ""],
            ["Terminals", data.stats?.terminals ?? ""],
            ["Productions", data.stats?.productions ?? ""],
            ["Nullable Symbols", (data.nullableSymbols || []).join(", ") || "None"],
            ["Conflicts", (data.conflicts || []).length],
        ]);

        heading("Original Grammar");
        linesBlock(data.originalGrammar || []);
        heading("Grammar after Left Recursion");
        linesBlock(data.leftRecursion || []);
        heading("Grammar after Left Factoring");
        linesBlock(data.leftFactoring || []);
        heading("FIRST Sets");
        mapTable(data.first);
        heading("FOLLOW Sets");
        mapTable(data.follow);
        heading("LL(1) Parsing Table");
        parsingTable();
        heading("Parser Simulation");
        simulationTable();
        heading("Final Result");
        paragraph(data.accepted ? "Accepted. The input string is valid for this grammar." : "Rejected. The parser could not accept the input string.");

        if (Array.isArray(data.conflicts) && data.conflicts.length) {
            heading("Conflicts");
            linesBlock(data.conflicts);
        }

        if (Array.isArray(data.parseErrors) && data.parseErrors.length) {
            heading("Parser Errors");
            linesBlock(data.parseErrors);
        }

        newPage();

        pages.forEach((page, index) => {
            page.push(`BT /F1 9 Tf ${color("#64748b")} rg ${pageWidth - 116} 32 Td (Page ${index + 1} of ${pages.length}) Tj ET`);
            page.push(`BT /F1 9 Tf ${color("#64748b")} rg ${margin} 32 Td (ParseCraft Compiler Report) Tj ET`);
        });

        const objects = [
            "<< /Type /Catalog /Pages 2 0 R >>",
            "",
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
            "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
        ];
        const firstPageObject = 6;
        const kids = [];

        pages.forEach((page, index) => {
            const contentObject = firstPageObject + index * 2;
            const pageObject = contentObject + 1;
            const stream = page.join("\n");
            objects[contentObject - 1] = `<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`;
            objects[pageObject - 1] = `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${pageWidth} ${pageHeight}] /Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> /Contents ${contentObject} 0 R >>`;
            kids.push(`${pageObject} 0 R`);
        });

        objects[1] = `<< /Type /Pages /Kids [${kids.join(" ")}] /Count ${pages.length} >>`;

        let pdf = "%PDF-1.4\n";
        const offsets = [0];
        objects.forEach((object, index) => {
            offsets.push(pdf.length);
            pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
        });

        const xref = pdf.length;
        pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
        offsets.slice(1).forEach((offset) => {
            pdf += `${String(offset).padStart(10, "0")} 00000 n \n`;
        });
        pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`;

        return new Blob([pdf], { type: "application/pdf" });
    }

    function downloadBlob(filename, blob) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    }

    sampleButtons.forEach((button) => {
        button.addEventListener("click", () => loadSample(button.dataset.sample));
    });

    if (themeToggle) {
        updateThemeButton();
        themeToggle.addEventListener("click", () => {
            const isDark = document.body.classList.toggle("dark-mode");
            localStorage.setItem("ParseCraft-theme", isDark ? "dark" : "light");
            updateThemeButton();
        });
    }

    cards.forEach((card, index) => {
        card.style.animationDelay = `${Math.min(index * 70, 480)}ms`;
        card.classList.add("fade-in");
    });

    setExplanationPanels();

    if (pipelineStages.length) {
        animatePipeline();
    }

    if (consoleLines.length) {
        animateConsole();
    }

    if (downloadReport) {
        downloadReport.addEventListener("click", () => {
            const reportData = readReportData();
            if (!reportData) {
                return;
            }

            downloadBlob("ParseCraft_Report.pdf", createPdfReport(reportData));
        });
    }

    if (grammarInput && !grammarInput.value.trim()) {
        loadSample("arithmetic");
    }

    if (results) {
        results.scrollIntoView({ behavior: "smooth", block: "start" });
    }
});
