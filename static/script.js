const form = document.getElementById("chat-form");
const chatBox = document.getElementById("chat-box");
const generateBtn = document.getElementById("generate-site-btn");
const themeSelect = document.getElementById("theme-select");

function addMessage(content, sender) {
  const message = document.createElement("div");
  message.classList.add("message", sender);
  message.innerHTML = content;
  chatBox.appendChild(message);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function addLoadingBubble() {
  const loading = document.createElement("div");
  loading.classList.add("message", "bot");
  loading.id = "loading";
  loading.innerHTML = "💭 Thinking...";
  chatBox.appendChild(loading);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function removeLoadingBubble() {
  const loading = document.getElementById("loading");
  if (loading) loading.remove();
}

let lastAIResponse = null;
let lastUserInput = null;

// Prevent double submissions
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (form.dataset.submitting === "true") return;
  form.dataset.submitting = "true";

  const industry = document.getElementById("industry").value;
  const goals = document.getElementById("goals").value;
  const style = themeSelect.value; 
  const projectDescriptions = document.getElementById("project-descriptions").value;

  const competitors = document
    .getElementById("competitors")
    .value.split(",")
    .map((c) => c.trim())
    .filter((c) => c);

  lastUserInput = { industry, style, goals, competitors, projectDescriptions };

  const userMessage = `
    Industry: <strong>${industry}</strong><br>
    Theme: <strong>${style}</strong><br>
    Goals: <strong>${goals}</strong>
    Projects: <strong>${projectDescriptions}</strong><br>
  `;

  addMessage(userMessage, "user");

  addLoadingBubble();

  try {
    const res = await fetch("/generate-portfolio-advice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lastUserInput),
    });

    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }

    const data = await res.json();
    removeLoadingBubble();

    lastAIResponse = data; // Save for generating site

    const botMessage = `
      <strong>📋 Copywriting Advice:</strong><br>${data.copywriting.replace(/\n/g, "<br>")}<br><br>
      <strong>🔍 SEO Tips:</strong> ${data.seo_tips.recommended_keywords.join(", ")}<br>
      <strong>🎨 Design Guidelines:</strong><br>
      ${data.design_guidelines.map((g) => `• ${g}`).join("<br>")}
    `;

    addMessage(botMessage, "bot");

    // Show the generate site button
    generateBtn.style.display = "block";
  } catch (err) {
    removeLoadingBubble();
    addMessage(`❌ Error: ${err.message}`, "bot");
  } finally {
    // Do not reset the form immediately — keep values so user can tweak theme or regenerate
    form.dataset.submitting = "false";
  }
});

// Generate the real website
generateBtn.addEventListener("click", async () => {
  if (!lastAIResponse || !lastUserInput) {
    addMessage("⚠️ No AI response to generate site from. Run the assistant first.", "bot");
    return;
  }

  const theme = themeSelect.value;
  const payload = {
    industry: lastUserInput.industry,
    style: theme,
    goals: lastUserInput.goals,
    competitors: lastUserInput.competitors,
    project_descriptions: lastUserInput.projectDescriptions,
    ai_copy: lastAIResponse.copywriting,
    seo_tips: lastAIResponse.seo_tips,
    design_guidelines: lastAIResponse.design_guidelines,
    theme: theme
  };

  addMessage("🛠️ Building your site...", "bot");

  try {
    const res = await fetch("/generate-full-site", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`Build failed: ${res.status}`);
    }

    const json = await res.json();
    addMessage(`✅ Site generated: <a href="${json.site_url}" target="_blank">Open site</a>`, "bot");

    // Open the generated site in a new tab
    window.open(json.site_url, "_blank");
  } catch (err) {
    addMessage(`❌ Error generating site: ${err.message}`, "bot");
  }
});
