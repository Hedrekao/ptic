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
        className='antialiased bg-slate-100'
      >
          <h1 className='text-3xl font-semibold tracking-tight my-12 w-full text-center'>Hierarchical image classification</h1>
        {children}
      </body>
    </html>
  );
}
