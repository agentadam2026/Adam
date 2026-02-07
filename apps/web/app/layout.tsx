import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Adam",
  description: "Adam's reading trails and canonical notes"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
