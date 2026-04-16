#!/usr/bin/env python3

import cv2
import numpy as np
from collections import deque
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import threading
import time


class AutoTicTacToeDetector(Node):

    def __init__(self):
        super().__init__('tictactoe_detector')

        # ---------------- Parameters ----------------
        self.declare_parameter('camera_id', 4)
        self.declare_parameter('grid_size', 900)
        self.declare_parameter('confidence_threshold', 3)
        self.declare_parameter('history_size', 7)
        self.declare_parameter('empty_threshold_ratio', 0.02)

        self.camera_id = self.get_parameter('camera_id').value
        self.grid_size = self.get_parameter('grid_size').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.empty_threshold_ratio = self.get_parameter('empty_threshold_ratio').value
        history_size = self.get_parameter('history_size').value

        # ---------------- ROS ----------------
        self.board_publisher = self.create_publisher(String, '/tictactoe/state', 10)

        # ---------------- CV ----------------
        self.cell_history = [[deque(maxlen=history_size) for _ in range(3)] for _ in range(3)]
        self.stable_board = [['.' for _ in range(3)] for _ in range(3)]

        self.frame_count = 0

        self.get_logger().info("TicTacToe Detector FINAL (p=publish, q=quit) Started")

    # ==========================================================
    def get_square_homography(self, frame):

        # 1. Preprocessing
        # print("image shape" + str(frame.shape))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)

        # 2. Find the Grid Contour
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter for the largest square-like contour
        best_cnt = None
        max_area = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 1000:  # Minimum size threshold
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                if len(approx) == 4 and area > max_area:
                    best_cnt = approx
                    max_area = area

        if best_cnt is not None:
            # 3. Perspective Transform (Warp)
            # Reorder points to [top-left, top-right, bottom-right, bottom-left]
            pts = best_cnt.reshape(4, 2)
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]

            side = 300  # Desired size of the flattened grid
            dst = np.array([[0, 0], [side - 1, 0], [side - 1, side - 1], [0, side - 1]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(gray, M, (side, side))

            warped = cv2.rotate(warped, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # 4. Isolate the 9 Squares
            numbered_warp = warped.copy()
            squares = []
            cell_size = side // 3
            for r in range(3):
                for c in range(3):
                    x1, y1 = c * cell_size, r * cell_size
                    x2, y2 = (c + 1) * cell_size, (r + 1) * cell_size
                    square = warped[y1:y2, x1:x2]
                    squares.append(square)

                    cv2.putText(numbered_warp, f"{r*3+c}", (x1 + 10, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow("numbered warp", numbered_warp)

            return warped, squares

        return None, None

    # ==========================================================
    def detect_symbol(self, cell_img):
        # 1. Handle Grayscale
        if len(cell_img.shape) == 3:
            cell_img = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY)

        # 2. Crop 15 pixels from each side to kill the grid lines
        h, w = cell_img.shape
        margin = 10
        if h > 2 * margin and w > 2 * margin:
            cell_img = cell_img[margin:h - margin, margin:w - margin]

        # 3. Aggressive Denoising
        # Median blur is excellent for 'salt and pepper' camera noise
        # cell_img = cv2.medianBlur(cell_img, 3)

        # 4. Adaptive Thresholding
        # Increased 'C' constant (10) to ignore light gray noise
        # _, thresh = cv2.threshold(cell_img, 200, 255, cv2.THRESH_BINARY_INV)
        thresh = cv2.adaptiveThreshold(cell_img, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 10)

        # 5. Morphological Closing
        # This 'welds' broken lines together—crucial for low-quality video
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # 6. Find Contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return ".", thresh

        # Get the largest object in the square
        main_cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(main_cnt)

        # Ignore if the object is too small (noise)
        if area < 250:
            return ".", thresh

        # 7. Solidity Analysis (The "X vs O" Secret)
        hull = cv2.convexHull(main_cnt)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0

        # 8. Classification Logic
        # An 'O' is very solid (usually > 0.75).
        # An 'X' has big gaps between arms (usually < 0.55).
        if solidity > 0.75:
            return "O", thresh
        else:
            return "X", thresh

    # ==========================================================
    def update_board_state(self, warped):

        h, w = warped.shape[:2]
        cell_h, cell_w = h // 3, w // 3

        for r in range(3):
            for c in range(3):

                idx = r * 3 + c  # Explicit index (0–8)

                cell = warped[
                    r * cell_h:(r + 1) * cell_h,
                    c * cell_w:(c + 1) * cell_w
                ]

                symbol, thresh_img = self.detect_symbol(cell)
                cv2.imshow(str(idx), thresh_img)
                cv2.moveWindow(str(idx), (c+1)*85, (r+1)*135)  # (x, y) in screen coordinates

                self.cell_history[r][c].append(symbol)

                counts = {}
                for s in self.cell_history[r][c]:
                    counts[s] = counts.get(s, 0) + 1

                best = max(counts, key=counts.get)

                if counts[best] >= self.confidence_threshold:
                    self.stable_board[r][c] = best

    # ==========================================================
    def get_board_string(self):
        """Return board as continuous uppercase string (0–8 indexing)"""

        values = ['.'] * 9

        for r in range(3):
            for c in range(3):

                idx = r * 3 + c

                symbol = self.stable_board[r][c]

                if symbol in ['x', 'X']:
                    values[idx] = 'X'
                elif symbol in ['o', 'O']:
                    values[idx] = 'O'
                else:
                    values[idx] = '.'

        return "".join(values)

    # ==========================================================
    def print_board_with_indices(self):
        """Debug: show index:value"""
        board_str = self.get_board_string()

        print("\nBoard (index:value):")
        for i in range(9):
            print(f"{i}:{board_str[i]}", end="  ")
            if (i + 1) % 3 == 0:
                print()

    # ==========================================================
    def publish_board(self):
        msg = String()
        msg.data = self.get_board_string()
        self.board_publisher.publish(msg)

        self.get_logger().info(f"PUBLISHED: {msg.data}")
        self.print_board_with_indices()


# ==============================================================
def main(args=None):
    rclpy.init(args=args)
    detector = AutoTicTacToeDetector()

    cap = cv2.VideoCapture(detector.camera_id)

    if not cap.isOpened():
        detector.get_logger().error("Camera not found")
        detector.destroy_node()
        rclpy.shutdown()
        return

    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(detector)

    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()

    try:
        while rclpy.ok():

            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            warped, squares = detector.get_square_homography(frame)

            if warped is not None:
                detector.frame_count += 1

                if detector.frame_count % 2 == 0:
                    detector.update_board_state(warped)

                #cv2.imshow("Grid Detector", warped)

            cv2.imshow("Frame Detector", frame)
            # detector.print_board_with_indices()

            key = cv2.waitKey(1) & 0xFF

            if key == ord('p'):
                detector.publish_board()

            elif key == ord('q'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

