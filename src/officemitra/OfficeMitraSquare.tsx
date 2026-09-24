import React from "react";
import { OfficeMitraVideo } from "./OfficeMitraVideo";

export const OfficeMitraSquare: React.FC = () => {
  return (
    <div
      style={{
        width: 1080,
        height: 1080,
        backgroundColor: "#070b16",
        overflow: "hidden",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
      }}
    >
      <div
        style={{
          width: 1920,
          height: 1080,
          transform: "scale(0.82)",
          transformOrigin: "center center",
        }}
      >
        <OfficeMitraVideo />
      </div>
    </div>
  );
};
