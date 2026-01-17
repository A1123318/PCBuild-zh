// web/assets/js/reset-password.js
const form = document.getElementById("reset-form");
const passwordInput = document.getElementById("password");
const passwordConfirmInput = document.getElementById("password-confirm");
const resetBtn = document.getElementById("reset-btn");
const errorEl = document.getElementById("error");

const passwordField = document.querySelector('[data-field="password"]');
const passwordConfirmField = document.querySelector('[data-field="password-confirm"]');

function clearResetToken() {
try { sessionStorage.removeItem("pcbuild_reset_token"); } catch {}
}

function refreshGlobalErrorFromFields() {
const fields = [passwordField, passwordConfirmField];
const hasError = fields.some((f) => f && f.classList.contains("field-error"));
if (!hasError) errorEl.textContent = "";
}

function clearSingleFieldError(field) {
if (!field) return;
field.classList.remove("field-error");
const msgEl = field.querySelector(".field-error-text");
if (msgEl) msgEl.textContent = "";
refreshGlobalErrorFromFields();
}

function setFieldError(field, message) {
if (!field) return;
field.classList.add("field-error");
const msgEl = field.querySelector(".field-error-text");
if (msgEl) msgEl.textContent = message || "";
}

function getToken() {
// 1) 先看 URL query（首次從 email 進來會帶 token）
const params = new URLSearchParams(window.location.search);
const tokenFromUrl = params.get("token");

// 2) 存到 sessionStorage 後把 URL token 移除，降低暴露風險
try {
    if (tokenFromUrl) {
    sessionStorage.setItem("pcbuild_reset_token", tokenFromUrl);
    history.replaceState(null, "", "/reset-password.html");
    }
    return sessionStorage.getItem("pcbuild_reset_token") || "";
} catch (e) {
    return tokenFromUrl || "";
}
}

const token = getToken();
if (!token) {
// 缺 token：直接導向無效頁
clearResetToken();
window.location.href = "/reset-password-failed.html";
}

function validatePasswordField() {
if (!passwordField) return;
clearSingleFieldError(passwordField);
const value = passwordInput.value;

if (!value) {
    setFieldError(passwordField, "請填寫新密碼。");
    return;
}
if (value.length < 8) {
    setFieldError(passwordField, "密碼長度至少需 8 個字元。");
}
}

function validatePasswordConfirmField() {
if (!passwordConfirmField) return;
clearSingleFieldError(passwordConfirmField);
const v1 = passwordInput.value;
const v2 = passwordConfirmInput.value;

if (!v2) {
    setFieldError(passwordConfirmField, "請再次輸入新密碼。");
    return;
}
if (v1 !== v2) {
    setFieldError(passwordConfirmField, "兩次密碼輸入不一致。");
}
}

passwordInput.addEventListener("blur", validatePasswordField);
passwordConfirmInput.addEventListener("blur", validatePasswordConfirmField);

form.addEventListener("submit", async (e) => {
e.preventDefault();
errorEl.textContent = "";

validatePasswordField();
validatePasswordConfirmField();

const hasError =
    (passwordField && passwordField.classList.contains("field-error")) ||
    (passwordConfirmField && passwordConfirmField.classList.contains("field-error"));

if (hasError) {
    errorEl.textContent = "請修正紅色標示的欄位。";
    return;
}

const newPassword = passwordInput.value;

resetBtn.disabled = true;
const originalText = resetBtn.textContent;
resetBtn.textContent = "處理中…";

try {
    const resp = await fetch("/api/auth/reset-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
    body: JSON.stringify({ token, password: newPassword }),
    });

    let data = null;
    try { data = await resp.json(); } catch { data = null; }

    if (!resp.ok) {
    // 下面三個頁面你後續會建立；先預留導向邏輯
    if (resp.status === 409 || resp.status === 410) {
        clearResetToken();
        window.location.href = "/reset-password-failed.html";
        return;
    }
    if (resp.status === 400) {
        const errors = data?.detail?.errors || {};
        const hasPasswordErr = !!errors.password;

        if (hasPasswordErr) setFieldError(passwordField, String(errors.password));
        if (errors.token) {
        clearResetToken();
        window.location.href = "/reset-password-failed.html";
        return;
        }

        // 有欄位錯誤時，不顯示 global 失敗訊息，讓使用者專注修正紅框欄位
        errorEl.textContent = hasPasswordErr ? "" : "重設密碼失敗，請稍後再試。";
    }else{
        errorEl.textContent = "重設密碼失敗，請稍後再試。";
    }
    return;
    }

    // 成功：清除 token，導回登入頁（不自動登入）
    try { sessionStorage.removeItem("pcbuild_reset_token"); } catch {}
    window.location.href = "/login.html";
} catch (err) {
    console.error("reset-password invalid:", err);
    errorEl.textContent = "重設密碼失敗，請稍後再試。";
} finally {
    resetBtn.disabled = false;
    resetBtn.textContent = originalText;
}
});