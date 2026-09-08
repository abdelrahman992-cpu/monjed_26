import { Resend } from "resend";
import dotenv from "dotenv";

dotenv.config();

const resend = new Resend(process.env.RESEND_API_KEY);

export async function sendOtpEmail(toEmail, otpCode) {
  try {
    const data = await resend.emails.send({
      from: "MONJED System <onboarding@resend.dev>", // يمكنك تغيير الاسم هنا
      to: [toEmail], // يرسل لأي إيميل يدخله المستخدم أو لجنة التحكيم
      subject: "MONJED - Your Verification Code",
      html: `
        <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #0f172a; color: #ffffff; border-radius: 8px;">
          <h2 style="color: #f59e0b; margin-bottom: 10px;">MONJED Verification</h2>
          <p style="font-size: 15px; color: #cbd5e1;">Use the following 6-digit code to complete your registration:</p>
          <div style="font-size: 28px; font-weight: bold; letter-spacing: 4px; color: #f59e0b; padding: 12px 0;">
            ${otpCode}
          </div>
          <p style="font-size: 12px; color: #64748b; margin-top: 20px;">If you did not request this code, please ignore this email.</p>
        </div>
      `,
    });
    return { success: true, data };
  } catch (error) {
    console.error("Failed to send OTP email:", error);
    // نرجع false ولكن دون إيقاف السيرفر ليظل الماستر كود شغال كأمان
    return { success: false, error };
  }
}