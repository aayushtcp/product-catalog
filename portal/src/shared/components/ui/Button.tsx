import type { ButtonHTMLAttributes } from "react";

type ButtonVariant = "ghost" | "primary";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
};

const variantClasses: Record<ButtonVariant, string> = {
  ghost: "text-navy cursor-pointer hover:bg-dusk-100",
  primary:
    "bg-sunset cursor-pointer font-bold text-white transition-colors hover:bg-sunset-600",
};

export default function Button({
  variant = "ghost",
  className = "",
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`${variantClasses[variant]} ${className}`.trim()}
      {...props}
    />
  );
}
