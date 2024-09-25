import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hierarchical image classification",
  description: "Hierarchical image classification by Stibo Systems",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
