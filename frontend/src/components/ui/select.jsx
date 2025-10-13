import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useRef,
} from "react";
import { createPortal } from "react-dom";
import { ChevronDown } from "lucide-react";

const SelectContext = createContext();

export const Select = ({
  value,
  onValueChange,
  defaultValue,
  children,
  ...props
}) => {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const [isOpen, setIsOpen] = useState(false);
  const currentValue = value !== undefined ? value : internalValue;
  const selectRef = useRef(null);

  const handleValueChange = (newValue) => {
    if (value === undefined) {
      setInternalValue(newValue);
    }
    if (onValueChange) {
      onValueChange(newValue);
    }
    setIsOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (selectRef.current && !selectRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  return (
    <SelectContext.Provider
      value={{
        value: currentValue,
        onValueChange: handleValueChange,
        isOpen,
        setIsOpen,
      }}
    >
      <div ref={selectRef} className="relative" {...props}>
        {children}
      </div>
    </SelectContext.Provider>
  );
};

export const SelectTrigger = ({ className = "", children, ...props }) => {
  const { isOpen, setIsOpen } = useContext(SelectContext);

  return (
    <button
      type="button"
      className={`flex h-10 w-full items-center justify-between rounded-md border border-gray-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsOpen(!isOpen);
      }}
      {...props}
    >
      {children}
      <ChevronDown
        className={`h-4 w-4 opacity-50 transition-transform ${
          isOpen ? "rotate-180" : ""
        }`}
      />
    </button>
  );
};

export const SelectValue = ({ placeholder, className = "", ...props }) => {
  const { value } = useContext(SelectContext);

  return (
    <span className={`block truncate ${className}`} {...props}>
      {value || placeholder}
    </span>
  );
};

export const SelectContent = ({ className = "", children, ...props }) => {
  const { isOpen } = useContext(SelectContext);

  if (!isOpen) return null;

  return (
    <div
      className={`mt-1 max-h-60 w-full overflow-auto rounded-md border border-gray-300 bg-white text-gray-900 shadow-lg ${className}`}
      style={{
        position: "absolute",
        top: "100%",
        left: 0,
        right: 0,
        zIndex: 99999,
        backgroundColor: "white",
        boxShadow: "0 10px 25px rgba(0,0,0,0.3)",
      }}
      {...props}
    >
      {children}
    </div>
  );
};

export const SelectItem = ({
  value,
  className = "",
  children,
  disabled,
  ...props
}) => {
  const { onValueChange } = useContext(SelectContext);

  return (
    <div
      className={`relative flex w-full cursor-pointer select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none hover:bg-gray-100 hover:text-gray-900 focus:bg-gray-100 focus:text-gray-900 ${
        disabled ? "pointer-events-none opacity-50" : ""
      } ${className}`}
      onClick={() => !disabled && onValueChange(value)}
      {...props}
    >
      {children}
    </div>
  );
};
