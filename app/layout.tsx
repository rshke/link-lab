import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "智能实验室设备孪生",
  description: "实验室设备、机器人、实验步骤和异常状态的实时孪生页面。",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">{children}</body>
    </html>
  );
}
