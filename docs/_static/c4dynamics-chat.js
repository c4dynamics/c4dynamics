document.addEventListener("DOMContentLoaded", () => {
    const ENDPOINT =
        "https://f2593d8b-bdf2-4eaa-b996-45e4292e2c8d.search.ai.cloudflare.com/chat/completions";

    // =========================================================
    // Conversation history
    // =========================================================

    const SYSTEM_PROMPT =
        "You are the c4dynamics documentation assistant. " +
        "Answer questions using the c4dynamics documentation provided by the retrieval system. " +
        "Be technically precise and do not invent APIs, functionality, or documentation facts. " +
        "This is a multi-turn conversation. Use the previous messages to understand follow-up questions and resolve references such as 'it', 'this', 'that', 'the first one', 'the third one', 'these variables', etc. " +
        "When a follow-up question refers to something discussed earlier, preserve that context when interpreting the user's question and when retrieving relevant documentation. " +
        "Prefer information explicitly supported by the documentation over general knowledge. " +
        "If the documentation does not contain the answer, say that you cannot find it in the documentation. " +
        "Use Markdown when appropriate, especially for headings, lists, inline code, and code examples.";

    const conversationHistory = [
        {
            role: "system",
            content: SYSTEM_PROMPT
        }
    ];

    // =========================================================
    // Helpers
    // =========================================================

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function renderMarkdown(markdown) {
        let text = String(markdown || "").replace(/\r\n/g, "\n");

        // Temporarily protect fenced code blocks
        const codeBlocks = [];

        text = text.replace(
            /```(?:python|py|javascript|js|json|bash|shell|text)?\n?([\s\S]*?)```/gi,
            (_, code) => {
                const index = codeBlocks.length;

                codeBlocks.push(
                    `<pre class="c4d-code-block"><code>${escapeHtml(
                        code.trim()
                    )}</code></pre>`
                );

                return `\n@@CODEBLOCK_${index}@@\n`;
            }
        );

        // Escape everything before adding safe formatting
        text = escapeHtml(text);

        // Headings
        text = text.replace(
            /^### (.+)$/gm,
            '<h4 class="c4d-md-h4">$1</h4>'
        );

        text = text.replace(
            /^## (.+)$/gm,
            '<h3 class="c4d-md-h3">$1</h3>'
        );

        text = text.replace(
            /^# (.+)$/gm,
            '<h2 class="c4d-md-h2">$1</h2>'
        );

        // Bold
        text = text.replace(
            /\*\*(.+?)\*\*/g,
            "<strong>$1</strong>"
        );

        // Italic
        text = text.replace(
            /(?<!\*)\*([^*\n]+)\*(?!\*)/g,
            "<em>$1</em>"
        );

        // Inline code
        text = text.replace(
            /`([^`\n]+)`/g,
            '<code class="c4d-inline-code">$1</code>'
        );

        // Links — only allow http(s)
        text = text.replace(
            /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
            '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
        );

        // Unordered lists
        text = text.replace(
            /^(?:[-*]) (.+)$/gm,
            '<li>$1</li>'
        );

        text = text.replace(
            /((?:<li>.*<\/li>\n?)+)/g,
            '<ul>$1</ul>'
        );

        // Ordered lists
        text = text.replace(
            /^\d+\.\s+(.+)$/gm,
            '<li>$1</li>'
        );

        // Paragraphs
        const blocks = text
            .split(/\n{2,}/)
            .map(block => block.trim())
            .filter(Boolean);

        text = blocks
            .map(block => {
                if (
                    block.startsWith("<h2") ||
                    block.startsWith("<h3") ||
                    block.startsWith("<h4") ||
                    block.startsWith("<ul>") ||
                    block.startsWith("<pre") ||
                    block.startsWith("@@CODEBLOCK_")
                ) {
                    return block;
                }

                return `<p>${block.replace(/\n/g, "<br>")}</p>`;
            })
            .join("\n");

        // Restore code blocks
        text = text.replace(
            /@@CODEBLOCK_(\d+)@@/g,
            (_, index) => codeBlocks[Number(index)]
        );

        return text;
    }

    // =========================================================
    // Button
    // =========================================================

    const button = document.createElement("button");
    button.id = "c4d-chat-button";
    button.setAttribute("aria-label", "Ask c4dynamics");
    button.innerHTML = `
        <span class="c4d-button-icon">✦</span>
        <span>Ask c4dynamics</span>
    `;

    document.body.appendChild(button);

    // =========================================================
    // Chat window
    // =========================================================

    const widget = document.createElement("div");
    widget.id = "c4d-chat-widget";

    widget.innerHTML = `
        <div class="c4d-chat-header">
            <div class="c4d-chat-title">
                <div class="c4d-chat-logo">C4</div>
                <div>
                    <div class="c4d-chat-title-main">Ask c4dynamics</div>
                    <div class="c4d-chat-title-sub">Documentation assistant</div>
                </div>
            </div>

            <button
                id="c4d-chat-close"
                class="c4d-chat-close"
                aria-label="Close chat"
            >×</button>
        </div>

        <div id="c4d-chat-messages">
            <div class="c4d-message c4d-assistant">
                <div class="c4d-message-label">c4dynamics</div>
                <div class="c4d-message-content">
                    Hi! Ask me anything about c4dynamics.
                </div>
            </div>
        </div>

        <div class="c4d-chat-input-area">
            <div class="c4d-chat-input">
                <input
                    id="c4d-chat-input"
                    type="text"
                    placeholder="Ask about c4dynamics..."
                    autocomplete="off"
                />

                <button
                    id="c4d-chat-send"
                    aria-label="Send message"
                >↑</button>
            </div>

            <div class="c4d-chat-footer">
                Answers are based on the c4dynamics documentation.
            </div>
        </div>
    `;

    document.body.appendChild(widget);

    // =========================================================
    // Elements
    // =========================================================

    const messages = document.getElementById("c4d-chat-messages");
    const input = document.getElementById("c4d-chat-input");
    const send = document.getElementById("c4d-chat-send");
    const close = document.getElementById("c4d-chat-close");

    // =========================================================
    // Open / close
    // =========================================================

    button.addEventListener("click", () => {
        widget.classList.add("open");
        input.focus();
    });

    close.addEventListener("click", () => {
        widget.classList.remove("open");
    });

    // =========================================================
    // Message handling
    // =========================================================

    function addMessage(text, type, render = false) {
        const message = document.createElement("div");
        message.className = `c4d-message c4d-${type}`;

        const label = document.createElement("div");
        label.className = "c4d-message-label";
        label.textContent =
            type === "user" ? "You" : "c4dynamics";

        const content = document.createElement("div");
        content.className = "c4d-message-content";

        if (render) {
            content.innerHTML = renderMarkdown(text);
        } else {
            content.textContent = text;
        }

        message.appendChild(label);
        message.appendChild(content);

        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;

        return message;
    }

    // =========================================================
    // Send
    // =========================================================

    async function sendMessage() {
        const question = input.value.trim();

        if (!question) {
            return;
        }

        input.value = "";

        // Display user's message
        addMessage(question, "user");

        // Add user message to conversation history
        conversationHistory.push({
            role: "user",
            content: question
        });

        // Thinking indicator
        const thinking = addMessage("Thinking…", "assistant");
        thinking.classList.add("c4d-thinking");

        send.disabled = true;
        input.disabled = true;

        try {
            const response = await fetch(ENDPOINT, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    messages: conversationHistory
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            const answer =
                data.choices?.[0]?.message?.content ||
                data.result?.response ||
                "Sorry, I couldn't generate an answer.";

            // Add assistant response to conversation history
            conversationHistory.push({
                role: "assistant",
                content: answer
            });

            const content =
                thinking.querySelector(".c4d-message-content");

            thinking.classList.remove("c4d-thinking");

            content.innerHTML = renderMarkdown(answer);

            messages.scrollTop = messages.scrollHeight;

        } catch (error) {
            console.error("c4dynamics chatbot error:", error);

            // Remove the user message from history because
            // the request failed and the model never saw it.
            conversationHistory.pop();

            const content =
                thinking.querySelector(".c4d-message-content");

            thinking.classList.remove("c4d-thinking");

            content.textContent =
                "Sorry, the documentation assistant is currently unavailable.";
        }

        send.disabled = false;
        input.disabled = false;
        input.focus();
    }

    // =========================================================
    // Events
    // =========================================================

    send.addEventListener("click", sendMessage);

    input.addEventListener("keydown", event => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
});
