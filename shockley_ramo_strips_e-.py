from manim import *
import numpy as np

class ShockleyRamoStripDetector_eMinus(Scene):
    """
    Animation showing how a moving charge induces signals in multiple 
    strip electrodes, allowing position reconstruction.
    
    This demonstrates the principle behind silicon strip detectors
    used in particle physics experiments.
    """
    
    def construct(self):
        # Parameters
        num_strips = 5
        strip_width = 1.0
        strip_height = 0.25
        strip_gap = 0.15  # Gap between strips
        detector_depth = 3.0  # Distance from strips to ground
        charge_radius = 0.15
        
        total_width = num_strips * strip_width + (num_strips - 1) * strip_gap
        
        # Colors for each strip
        strip_colors = [RED, ORANGE, YELLOW, GREEN, BLUE]
        
        # Create strip electrodes
        strips = VGroup()
        strip_labels = VGroup()
        for i in range(num_strips):
            x_pos = -total_width/2 + strip_width/2 + i * (strip_width + strip_gap)
            strip = Rectangle(
                width=strip_width,
                height=strip_height,
                fill_color=strip_colors[i],
                fill_opacity=0.8,
                stroke_color=WHITE
            ).move_to([x_pos, detector_depth/2, 0])
            strips.add(strip)
            
            label = MathTex(f"S_{i+1}", font_size=20).next_to(strip, UP, buff=0.1)
            strip_labels.add(label)
        
        # Ground plane
        ground = Rectangle(
            width=total_width + 1,
            height=strip_height,
            fill_color=GRAY,
            fill_opacity=0.8,
            stroke_color=WHITE
        ).move_to([0, -detector_depth/2, 0])
        ground_label = Text("Ground", font_size=20).next_to(ground, DOWN)
        
        # Create charge
        charge = Circle(
            radius=charge_radius,
            fill_color=WHITE,
            fill_opacity=1,
            stroke_color=YELLOW,
            stroke_width=2
        )
        charge_symbol = MathTex("-", font_size=20, color=BLACK).move_to(charge)
        charge_group = VGroup(charge, charge_symbol)
        
        # Charge trajectory: diagonal path across strips
        start_pos = np.array([-total_width/2 - 0.5, -detector_depth/2 + 0.5, 0])
        end_pos = np.array([total_width/2 + 0.5, detector_depth/2 - 0.5, 0])
        charge_group.move_to(start_pos)
        
        # Trajectory line (dashed)
        trajectory = DashedLine(start_pos, end_pos, color=WHITE, dash_length=0.1)
        
        # Current trackers for each strip
        current_trackers = [ValueTracker(0) for _ in range(num_strips)]
        
        # Current bar graphs for each strip
        bar_width = 0.3
        max_bar_height = 1.5
        bar_base_y = -detector_depth/2 - 1.5
        
        def create_bar(i):
            x_pos = -total_width/2 + strip_width/2 + i * (strip_width + strip_gap)
            height = max(0.01, abs(current_trackers[i].get_value()) * max_bar_height)
            bar = Rectangle(
                width=bar_width,
                height=height,
                fill_color=strip_colors[i],
                fill_opacity=0.8,
                stroke_color=WHITE
            )
            bar.move_to([x_pos, bar_base_y + height/2, 0])
            return bar
        
        current_bars = VGroup(*[
            always_redraw(lambda i=i: create_bar(i)) for i in range(num_strips)
        ])
        
        # Current value labels
        def create_current_label(i):
            x_pos = -total_width/2 + strip_width/2 + i * (strip_width + strip_gap)
            val = -1*current_trackers[i].get_value() #-1 because it's an electron (negative charge)
            return MathTex(f"{val:.2f}", font_size=16).move_to([x_pos, bar_base_y - 0.3, 0])
        
        current_labels = VGroup(*[
            always_redraw(lambda i=i: create_current_label(i)) for i in range(num_strips)
        ])
        
        # Title and equation
        title = Text("Strip Detector: Position Sensing", font_size=28).to_edge(UP)
        equation = MathTex(
            r"I_k = q \vec{v} \cdot \vec{E}_{w,k}",
            font_size=28
        ).next_to(title, DOWN)
        
        # Legend for current display
        current_title = Text("Induced Currents", font_size=20).move_to([0, bar_base_y - 0.8, 0])
        
        # Weighting field visualization (simplified - show field lines for middle strip only initially)
        # We'll animate this later
        
        # Build scene
        self.play(Write(title), run_time=0.5)
        self.play(Write(equation), run_time=0.5)
        
        self.play(
            *[Create(strip) for strip in strips],
            *[Write(label) for label in strip_labels],
            run_time=1
        )
        
        self.play(
            Create(ground),
            Write(ground_label),
            run_time=0.5
        )
        
        self.play(
            Create(trajectory),
            run_time=0.5
        )
        
        self.play(
            Write(current_title),
            *[Create(bar) for bar in current_bars],
            run_time=0.5
        )
        self.add(current_labels)
        
        self.play(FadeIn(charge_group), run_time=0.3)
        
        # Velocity arrow
        velocity_arrow = always_redraw(
            lambda: Arrow(
                charge_group.get_center(),
                charge_group.get_center() + normalize(end_pos - start_pos) * 0.6,
                buff=0,
                color=GREEN,
                stroke_width=2,
                max_tip_length_to_length_ratio=0.2
            )
        )
        self.play(GrowArrow(velocity_arrow), run_time=0.3)
        
        # Function to calculate induced current on each strip
        # Using simplified weighting field model for strip detectors
        def calculate_currents(charge_pos):
            currents = []
            for i in range(num_strips):
                strip_x = -total_width/2 + strip_width/2 + i * (strip_width + strip_gap)
                strip_y = detector_depth/2
                
                # Distance from charge to strip center
                dx = charge_pos[0] - strip_x
                dy = charge_pos[1] - strip_y
                
                # Simplified weighting field model:
                # Field is strongest directly below strip, falls off with distance
                # E_w ~ 1/r^2 behavior, pointing toward strip
                r_sq = dx**2 + dy**2 + 0.1  # Small offset to avoid singularity
                
                # Weighting field magnitude (simplified)
                E_w_mag = 1.0 / (r_sq + 0.5)
                
                # Direction: toward the strip
                E_w_dir = np.array([strip_x - charge_pos[0], strip_y - charge_pos[1], 0])
                E_w_dir_norm = E_w_dir / (np.linalg.norm(E_w_dir) + 0.01)
                
                # Velocity direction
                v_dir = normalize(end_pos - start_pos)
                
                # Induced current: I = q * v · E_w
                current = np.dot(v_dir, E_w_dir_norm) * E_w_mag
                
                # Only show significant currents when charge is in detector region
                if charge_pos[0] < -total_width/2 - 0.3 or charge_pos[0] > total_width/2 + 0.3:
                    current = 0
                if charge_pos[1] < -detector_depth/2 + 0.3 or charge_pos[1] > detector_depth/2 - 0.3:
                    current *= 0.3
                
                currents.append(current)
            return currents
        
        # Updater for currents
        def update_currents(mob):
            pos = charge_group.get_center()
            currents = calculate_currents(pos)
            for i, current in enumerate(currents):
                current_trackers[i].set_value(current)
        
        charge_group.add_updater(update_currents)
        
        # Main animation: charge moves diagonally across detector
        self.play(
            charge_group.animate.move_to(end_pos),
            run_time=8,
            rate_func=linear
        )
        
        charge_group.remove_updater(update_currents)
        
        # Reset currents
        for tracker in current_trackers:
            tracker.set_value(0)
        
        self.wait(1)
        
        # Show position reconstruction concept
        self.play(FadeOut(velocity_arrow), FadeOut(trajectory))
        
        recon_text = Text(
            "Peak current → Charge passed closest to that strip!",
            font_size=24,
            color=YELLOW
        ).to_edge(DOWN, buff=0.3)
        
        self.play(Write(recon_text), run_time=1)
        self.wait(2)


class ShockleyRamoWeightingFields_eMinus(Scene):
    """
    Show the weighting field concept for multiple electrodes.
    Each electrode has its own weighting field.
    """
    
    def construct(self):
        # Parameters
        num_strips = 3
        strip_width = 1.5
        strip_height = 0.3
        strip_gap = 0.3
        detector_depth = 3.0
        
        total_width = num_strips * strip_width + (num_strips - 1) * strip_gap
        strip_colors = [RED, GREEN, BLUE]
        
        # Create strips
        strips = VGroup()
        for i in range(num_strips):
            x_pos = -total_width/2 + strip_width/2 + i * (strip_width + strip_gap)
            strip = Rectangle(
                width=strip_width,
                height=strip_height,
                fill_color=strip_colors[i],
                fill_opacity=0.8,
                stroke_color=WHITE
            ).move_to([x_pos, detector_depth/2, 0])
            strips.add(strip)
        
        # Ground
        ground = Rectangle(
            width=total_width + 1,
            height=strip_height,
            fill_color=GRAY,
            fill_opacity=0.8,
            stroke_color=WHITE
        ).move_to([0, -detector_depth/2, 0])
        
        # Title
        title = Text("Weighting Fields for Each Electrode", font_size=32).to_edge(UP)
        
        self.play(Write(title))
        self.play(
            *[Create(strip) for strip in strips],
            Create(ground),
            run_time=1
        )
        
        # Show weighting field for each strip one at a time
        for idx in range(num_strips):
            strip_x = -total_width/2 + strip_width/2 + idx * (strip_width + strip_gap)
            
            # Explanation
            explanation = VGroup(
                MathTex(f"\\phi_{{w,{idx+1}}}:", font_size=28),
                Text(f"Strip {idx+1} at V=1", font_size=20),
                Text("Others at V=0", font_size=20),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            explanation.to_corner(UL).shift(DOWN * 0.8)
            
            # Highlight the active strip
            highlight = strips[idx].copy()
            highlight.set_fill(WHITE, opacity=0.3)
            highlight.set_stroke(WHITE, width=3)
            
            # Create field lines for this strip's weighting field
            field_lines = VGroup()
            for dx in np.linspace(-strip_width/3, strip_width/3, 3):
                for frac in [0.2, 0.4, 0.6, 0.8]:
                    y_start = -detector_depth/2 + strip_height/2 + 0.1
                    y_end = detector_depth/2 - strip_height/2 - 0.1
                    y = y_start + frac * (y_end - y_start)
                    
                    # Field lines curve toward the active strip
                    x_start = strip_x + dx * (1 - frac * 0.5)
                    
                    arrow = Arrow(
                        start=[x_start, y - 0.2, 0],
                        end=[x_start + (strip_x - x_start) * 0.1, y + 0.2, 0],
                        buff=0,
                        color=strip_colors[idx],
                        stroke_width=2,
                        max_tip_length_to_length_ratio=0.3
                    )
                    field_lines.add(arrow)
            
            # Add some curved field lines from sides
            for side in [-1, 1]:
                for frac in [0.3, 0.6]:
                    y_start = -detector_depth/2 + strip_height/2 + 0.1
                    y_end = detector_depth/2 - strip_height/2 - 0.1
                    y = y_start + frac * (y_end - y_start)
                    x = strip_x + side * (strip_width/2 + 0.5)
                    
                    arrow = Arrow(
                        start=[x, y - 0.15, 0],
                        end=[x - side * 0.15, y + 0.15, 0],
                        buff=0,
                        color=strip_colors[idx],
                        stroke_width=1.5,
                        max_tip_length_to_length_ratio=0.3
                    )
                    field_lines.add(arrow)
            
            field_label = MathTex(
                f"\\vec{{E}}_{{w,{idx+1}}}",
                font_size=28,
                color=strip_colors[idx]
            ).next_to(strips[idx], RIGHT, buff=0.5)
            
            self.play(
                Write(explanation),
                Create(highlight),
                run_time=0.5
            )
            
            self.play(
                *[GrowArrow(arrow) for arrow in field_lines],
                Write(field_label),
                run_time=1
            )
            
            self.wait(1.5)
            
            self.play(
                FadeOut(explanation),
                FadeOut(highlight),
                FadeOut(field_lines),
                FadeOut(field_label),
                run_time=0.5
            )
        
        # Final message
        final_text = VGroup(
            Text("Each strip has its own weighting field", font_size=24),
            MathTex(r"I_k = q \vec{v} \cdot \vec{E}_{w,k}", font_size=28),
            Text("→ Different strips see different currents!", font_size=24, color=YELLOW),
        ).arrange(DOWN, buff=0.3)
        final_text.to_edge(DOWN, buff=0.5)
        
        self.play(Write(final_text), run_time=2)
        self.wait(2)


if __name__ == "__main__":
    # Render with: manim -pql shockley_ramo_strips_e-.py ShockleyRamoStripDetector_eMinus
    # Or: manim -pql shockley_ramo_strips_e-.py ShockleyRamoWeightingFields_eMinus
    pass
