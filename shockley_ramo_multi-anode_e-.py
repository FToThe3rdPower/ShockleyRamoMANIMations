from manim import *
import numpy as np

class ShockleyRamoMultiAnodeDetector_eMinus(Scene):
    """
    Animation showing how a moving charge induces signals in multiple
    anode electrodes, allowing position reconstruction.

    This demonstrates the principle behind multi-anode detectors
    used in particle physics experiments.
    """
    
    def construct(self):
        # Parameters
        num_anodes = 5
        anode_width = 1.5
        anode_height = 0.35
        anode_gap = 0.25
        detector_depth = 4.0
        charge_radius = 0.2
        right_offset = 1.5
        
        total_width = num_anodes * anode_width + (num_anodes - 1) * anode_gap
        
        # Colors for each anode
        anode_colors = [RED, ORANGE, YELLOW, GREEN, BLUE]
        
        # Create anode electrodes
        anodes = VGroup()
        anode_labels = VGroup()
        for i in range(num_anodes):
            x_pos = -total_width/2 + anode_width/2 + i * (anode_width + anode_gap) + right_offset
            anode = Rectangle(
                width=anode_width,
                height=anode_height,
                fill_color=anode_colors[i],
                fill_opacity=0.8,
                stroke_color=WHITE
            ).move_to([x_pos, detector_depth/2, 0])
            anodes.add(anode)
            
            label = MathTex(f"A_{i+1}", font_size=24).next_to(anode, UP, buff=0.1)
            anode_labels.add(label)
        
        # Ground plane
        ground = Rectangle(
            width=total_width + 1,
            height=anode_height,
            fill_color=GRAY,
            fill_opacity=0.8,
            stroke_color=WHITE
        ).move_to([right_offset, -detector_depth/2, 0])
        ground_label = Text("Ground", font_size=22).next_to(ground, DOWN, buff=0.1)
        
        # Create charge
        charge = Circle(
            radius=charge_radius,
            fill_color=YELLOW,
            fill_opacity=1,
            stroke_color=YELLOW,
            stroke_width=2
        )
        charge_symbol = MathTex("-", font_size=20, color=BLACK).move_to(charge)
        charge_group = VGroup(charge, charge_symbol)
        
        # Charge trajectory: diagonal path across anodes
        start_pos = np.array([-total_width/2 - 0.5 + right_offset, -detector_depth/2 + 0.5, 0])
        end_pos = np.array([total_width/2 + 0.5 +right_offset, detector_depth/2 - 0.5, 0])
        charge_group.move_to(start_pos)
        
        # Trajectory trace — built up as the charge moves (contrail style)
        trace = TracedPath(charge_group.get_center, stroke_color=WHITE, stroke_width=2)
        
        # Current trackers for each anode
        current_trackers = [ValueTracker(0) for _ in range(num_anodes)]
        
        # Current bar graphs for each anode (right panel)
        bar_width = 0.45
        bar_gap = 0.35
        max_bar_height = 3.0
        bar_base_y = -max_bar_height / 2
        bar_x_offset = -2.6
        current_label_offset = -6.0
        
        def create_bar(i):
            #x_pos = -total_width/2 + anode_width/2 + i * (anode_width + anode_gap) + bar_x_offset
            x_pos = -total_width/2 - anode_width/2 + i * (bar_width + bar_gap) + bar_x_offset
            height = max(0.01, abs(current_trackers[i].get_value()) * max_bar_height)
            bar = Rectangle(
                width=bar_width,
                height=height,
                fill_color=anode_colors[i],
                fill_opacity=0.8,
                stroke_color=WHITE
            )
            bar.move_to([x_pos, bar_base_y + height/2, 0])
            return bar
        
        current_bars = VGroup(*[
            always_redraw(lambda i=i: create_bar(i)) for i in range(num_anodes)
        ])
        
        # Current value labels
        def create_current_label(i):
            #x_pos = -total_width/2 + anode_width/2 + i * (anode_width + anode_gap) + bar_x_offset
            x_pos = -total_width/2 - anode_width/2 + i * (bar_width + bar_gap) + bar_x_offset - 0.01
            val = -1*current_trackers[i].get_value() #-1 because it's an electron (negative charge)
            return MathTex(f"{val:.2f}", font_size=20).move_to([x_pos, bar_base_y - 0.35, 0])
        
        current_labels = VGroup(*[
            always_redraw(lambda i=i: create_current_label(i)) for i in range(num_anodes)
        ])
        
        # equation on the left of the itle which is just above anodes (center); 
        equation = MathTex(r"I_k = q \vec{v} \cdot \vec{E}_{w,k}", font_size=32).move_to([-6.0, 2.4, 0])
        title = Text("Multi-Anode Detector: Position Sensing", font_size=22).next_to(anode_labels, UP, buff=0.1)
        
        # Legend for current display (right panel, above bars)
        current_title = Text("Induced Currents", font_size=22).move_to([current_label_offset, bar_base_y + max_bar_height + 0.15, 0])
        
        # Weighting field visualization (simplified - show field lines for middle anodes only initially)
        # We'll animate this later
        
        # Build scene
        self.play(Write(equation), run_time=0.5)
        self.play(Write(title), run_time=0.5)
        
        self.play(
            *[Create(anode) for anode in anodes],
            *[Write(label) for label in anode_labels],
            run_time=1
        )
        
        self.play(
            Create(ground),
            Write(ground_label),
            run_time=0.5
        )
        
        self.add(trace)
        
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
                charge_group.get_center() + normalize(end_pos - start_pos) * 0.8,
                buff=0,
                color=GREEN,
                stroke_width=2,
                max_tip_length_to_length_ratio=0.2
            )
        )
        self.play(GrowArrow(velocity_arrow), run_time=0.3)
        
        # Function to calculate induced current on each anode
        # Using simplified weighting field model for multi-anode detectors
        def calculate_currents(charge_pos):
            currents = []
            for i in range(num_anodes):
                anode_x = -total_width/2 + anode_width/2 + i * (anode_width + anode_gap) + right_offset
                anode_y = detector_depth/2

                # Distance from charge to anode center
                dx = charge_pos[0] - anode_x
                dy = charge_pos[1] - anode_y

                # Simplified weighting field model:
                # Field is strongest directly below anode, falls off with distance
                # E_w ~ 1/r^2 behavior, pointing toward anode
                r_sq = dx**2 + dy**2 + 0.1  # Small offset to avoid singularity

                # Weighting field magnitude (simplified)
                E_w_mag = 1.0 / (r_sq + 0.5)

                # Direction: toward the anode
                E_w_dir = np.array([anode_x - charge_pos[0], anode_y - charge_pos[1], 0])
                E_w_dir_norm = E_w_dir / (np.linalg.norm(E_w_dir) + 0.01)

                # Velocity direction
                v_dir = normalize(end_pos - start_pos)

                # Induced current: I = q * v · E_w
                current = np.dot(v_dir, E_w_dir_norm) * E_w_mag

                # Only show significant currents when charge is in detector region
                if charge_pos[0] < -total_width/2 - 0.3 + right_offset or charge_pos[0] > total_width/2 + 0.3 + right_offset:
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
        self.play(FadeOut(velocity_arrow), FadeOut(trace))
        
        recon_text = Text(
            "Peak current → Charge passed closest to that anode!",
            font_size=24,
            color=YELLOW
        ).move_to([current_label_offset, bar_base_y - 0.7, 0])
        
        self.play(Write(recon_text), run_time=1)
        self.wait(2)



class ShockleyRamoWeightingPotential_Center(Scene):
    """
    Equipotential lines of the weighting potential φ_w for the center anode
    of a 3-anode detector with equal-width electrodes: center at V=1,
    left and right grounded (V=0), ground plane at V=0. Uses Fourier cosine
    series satisfying Laplace's equation with Dirichlet BCs at x=±L and y=-d/2.
    """

    def construct(self):
        anode_width  = 3.5
        anode_gap    = 0.7
        anode_height = 0.4
        d = 4.0
        L = (3 * anode_width + 2 * anode_gap) / 2   # = 5.95; detector spans x: -L to +L

        w_sense = anode_width   # equal-width: sensing same as grounded flanks
        gap     = anode_gap

        # Center (sensing) electrode at x=0
        sense_anode = Rectangle(
            width=w_sense, height=anode_height,
            fill_color=YELLOW, fill_opacity=0.9,
            stroke_color=WHITE, stroke_width=2,
        ).move_to([0, d/2, 0])

        # Grounded flanks — equal width, separated by gap from center electrode
        flank_center = anode_width + gap   # = 4.2
        left_anode = Rectangle(
            width=w_sense, height=anode_height,
            fill_color=GRAY, fill_opacity=0.5,
            stroke_color=WHITE, stroke_width=1,
        ).move_to([-flank_center, d/2, 0])
        right_anode = Rectangle(
            width=w_sense, height=anode_height,
            fill_color=GRAY, fill_opacity=0.5,
            stroke_color=WHITE, stroke_width=1,
        ).move_to([+flank_center, d/2, 0])

        anodes = VGroup(left_anode, sense_anode, right_anode)
        anode_labels = VGroup(
            Text("Ground", font_size=20, color=GRAY).next_to(left_anode,  UP, buff=0.08),
            Text("Ground", font_size=20, color=GRAY).next_to(right_anode, UP, buff=0.08),
        )

        # Ground plane
        ground = Rectangle(
            width=2*L, height=anode_height,
            fill_color=GRAY, fill_opacity=0.7,
            stroke_color=WHITE, stroke_width=1,
        ).move_to([0, -d/2, 0])
        ground_label = Text("Ground", font_size=20).next_to(ground, DOWN, buff=0.1)

        title = Text(
            "Weighting Potential: Center Anode", font_size=26
        ).next_to(anode_labels, UP, buff=0.1)

        # Fourier cosine series for finite detector with Dirichlet BCs at x=±L, y=-d/2.
        # Eigenfunctions: cos(k_m * x),  k_m = (2m-1)*π/(2L)
        # phi(x,y) = Σ_m C_m * cos(k_m*x) * sinh(k_m*(y+d/2)) / sinh(k_m*d)
        # C_m = [4/((2m-1)π)] * sin((2m-1)*π*w_sense/(4L))
        N_terms = 80
        ms      = np.arange(1, N_terms + 1, dtype=float)
        kms     = (2*ms - 1) * np.pi / (2*L)
        C_ms    = (4 / ((2*ms - 1) * np.pi)) * np.sin((2*ms - 1) * np.pi * w_sense / (4*L))
        sigmas  = np.sinc((2*ms - 1) / (2*N_terms))  # Lanczos sigma: reduces Gibbs ringing
        C_ms   *= sigmas

        def phi_w(x, y):
            kms_y_d2 = kms * (y + d/2)
            kms_d    = kms * d
            ratios = np.where(
                kms_d > 20,
                np.exp(kms_y_d2 - kms_d),
                np.sinh(kms_y_d2) / np.sinh(kms_d),
            )
            return float(np.sum(C_ms * np.cos(kms * x) * ratios))

        # Contour levels spanning the weighting potential range from furthest to closest (least to greatest potential)
        levels = [0.007, 0.02, 0.05, 0.1, 0.2, 0.35, 0.55, 0.75] #[0.002, 0.007, 0.02, 0.05, 0.1, 0.2, 0.35, 0.55, 0.75]

        # Logarithmic color bar: 10^-3 to 10^0
        phi_log_min, phi_log_max = -3.0, 0.0
        bar_h, bar_w_px, n_seg = 3.5, 0.4, 40
        bar_x = -8.5
        bar_colors = color_gradient([BLUE_C, TEAL_C, GREEN_C, YELLOW, ORANGE, RED_C], n_seg)
        color_bar = VGroup(*[
            Rectangle(
                width=bar_w_px, height=bar_h / n_seg,
                fill_color=bar_colors[j], fill_opacity=0.9, stroke_width=0,
            ).move_to([bar_x, -bar_h/2 + (j + 0.5) * bar_h / n_seg, 0])
            for j in range(n_seg)
        ])

        # Decade tick marks at 10^-3, 10^-2, 10^-1, 10^0
        bar_ticks = VGroup()
        bar_tick_labels = VGroup()
        for exp in range(-3, 1):
            y_tick = -bar_h/2 + (exp - phi_log_min) / (phi_log_max - phi_log_min) * bar_h
            tick = Line(
                [bar_x + bar_w_px/2, y_tick, 0],
                [bar_x + bar_w_px/2 + 0.25, y_tick, 0],
                color=WHITE, stroke_width=2,
            )
            lbl = MathTex(f"10^{{{exp}}}", font_size=24).next_to(tick, RIGHT, buff=0.08)
            bar_ticks.add(tick)
            bar_tick_labels.add(lbl)

        bar_title = MathTex(r"\phi_{w,2}", font_size=32).next_to(color_bar, UP, buff=0.2)

        # Assign contour colors based on log-scale position of each level
        def level_to_color(lv):
            t = float(np.clip((np.log10(lv) - phi_log_min) / (phi_log_max - phi_log_min), 0, 1))
            return color_gradient([BLUE_C, TEAL_C, GREEN_C, YELLOW, ORANGE, RED_C], 101)[int(t * 100)]

        contour_colors = [level_to_color(lv) for lv in levels]

        equipotentials = [
            ImplicitFunction(
                lambda x, y, lv=level: phi_w(x, y) - lv,
                x_range=[-L, L],
                y_range=[-d/2, d/2],
                color=contour_colors[i],
                stroke_width=3,
            )
            for i, level in enumerate(levels)
        ]

        # Build scene
        self.play(Write(title), run_time=0.5)
        self.play(
            Create(color_bar),
            Create(bar_ticks), Write(bar_tick_labels), Write(bar_title),
            run_time=0.8,
        )
        self.play(
            *[Create(a) for a in anodes],
            *[Write(l) for l in anode_labels],
            Create(ground), Write(ground_label),
            run_time=1,
        )
        # Animate from highest potential (tight, near sensing anode) outward to lowest
        for curve in reversed(equipotentials):
            self.play(Create(curve), run_time=0.3)
        self.wait(2)


if __name__ == "__main__":
    pass
